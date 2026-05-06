"""
models/mf_gpu.py
Neural GPU-Accelerated Biased Matrix Factorization for IntelliRec
-----------------------------------------------------------------
Architecture: GMF dot-product path + non-linear MLP path (NeuMF-style)
Training:     All data pre-loaded to GPU VRAM -- eliminates CPU starvation
              ReduceLROnPlateau + LR warmup + AMP + gradient clipping
"""

import time
import numpy as np

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


# ---------------------------------------------------------------------------
# PyTorch model
# ---------------------------------------------------------------------------

class _NeuralMF(nn.Module):
    """
    Neural Matrix Factorization:
        score = dot(p, q)                   <- linear GMF path
              + MLP([p; q] -> 256->128->1)  <- non-linear path
              + b_u + b_i + b_global
    Trained on centred ratings (targets = rating - global_mean).
    Clamped to [-4, 4] at output; global_mean is added back at inference.
    """

    def __init__(self, n_users: int, n_items: int,
                 n_factors: int = 128, dropout: float = 0.2):
        super().__init__()
        self.user_emb    = nn.Embedding(n_users, n_factors)
        self.item_emb    = nn.Embedding(n_items, n_factors)
        self.user_bias   = nn.Embedding(n_users, 1)
        self.item_bias   = nn.Embedding(n_items, 1)
        self.global_bias = nn.Parameter(torch.zeros(1))
        self.drop        = nn.Dropout(dropout)

        # MLP non-linear interaction head
        mlp_in = n_factors * 2
        self.mlp = nn.Sequential(
            nn.Linear(mlp_in, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1, bias=False),
        )

        # Initialisation
        nn.init.normal_(self.user_emb.weight,  std=0.05)
        nn.init.normal_(self.item_emb.weight,  std=0.05)
        nn.init.zeros_(self.user_bias.weight)
        nn.init.zeros_(self.item_bias.weight)
        for m in self.mlp:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, u_ids: torch.Tensor, i_ids: torch.Tensor) -> torch.Tensor:
        p  = self.drop(self.user_emb(u_ids))    # (B, F)
        q  = self.drop(self.item_emb(i_ids))    # (B, F)
        bu = self.user_bias(u_ids).squeeze(1)   # (B,)
        bi = self.item_bias(i_ids).squeeze(1)   # (B,)

        dot     = (p * q).sum(dim=1)                              # linear path
        mlp_out = self.mlp(torch.cat([p, q], dim=1)).squeeze(1)  # non-linear path

        pred = dot + mlp_out + bu + bi + self.global_bias
        return torch.clamp(pred, -4.0, 4.0)


# ---------------------------------------------------------------------------
# Inference wrapper (pure numpy — no PyTorch at serve time)
# ---------------------------------------------------------------------------

class SurpriseCompatibleMF:
    """
    Holds trained factors as plain numpy arrays.
    predict(uid, iid).est is drop-in replacement for scikit-surprise SVD.
    """

    def __init__(self, user_factors, item_factors, user_bias, item_bias,
                 global_bias, user_to_idx, item_to_idx, global_mean,
                 mlp_weights=None):
        self.user_factors = np.asarray(user_factors, dtype=np.float32)
        self.item_factors = np.asarray(item_factors, dtype=np.float32)
        self.user_bias    = np.asarray(user_bias,    dtype=np.float32).ravel()
        self.item_bias    = np.asarray(item_bias,    dtype=np.float32).ravel()
        self.global_bias  = float(global_bias)
        self.global_mean  = float(global_mean)
        self.user_to_idx  = user_to_idx
        self.item_to_idx  = item_to_idx
        # MLP weights stored for inference (list of (W, b) tuples or None)
        self.mlp_weights  = mlp_weights

    def _mlp_forward(self, x: np.ndarray) -> float:
        """Run the saved MLP weights on a numpy vector."""
        if self.mlp_weights is None:
            return 0.0
        for W, b, act, norm_params in self.mlp_weights:
            x = x @ W.T + b
            if norm_params is not None:
                gamma, beta, mean, var = norm_params
                x = (x - mean) / np.sqrt(var + 1e-5) * gamma + beta
            if act == 'relu':
                x = np.maximum(0, x)
        return float(x.sum())

    def predict(self, uid, iid):
        class _Pred:
            __slots__ = ('est',)
            def __init__(self, est): self.est = float(est)

        score = self.global_mean + self.global_bias
        u_idx = self.user_to_idx.get(str(uid))
        i_idx = self.item_to_idx.get(str(iid))

        uf = self.user_factors[u_idx] if u_idx is not None else None
        itf = self.item_factors[i_idx] if i_idx is not None else None

        if u_idx is not None:
            score += float(self.user_bias[u_idx])
        if i_idx is not None:
            score += float(self.item_bias[i_idx])
        if uf is not None and itf is not None:
            score += float(np.dot(uf, itf))
            # MLP non-linear path
            if self.mlp_weights is not None:
                score += self._mlp_forward(np.concatenate([uf, itf]))
        return _Pred(float(np.clip(score, 1.0, 5.0)))

    def test(self, testset):
        class _Pred:
            __slots__ = ('uid', 'iid', 'r_ui', 'est')
            def __init__(self, uid, iid, r_ui, est):
                self.uid = uid; self.iid = iid
                self.r_ui = r_ui; self.est = est
        return [_Pred(u, i, r, self.predict(u, i).est) for u, i, r in testset]

    def compute_precision_recall_at_k(self, testset, k: int = 10,
                                      threshold: float = 3.5,
                                      max_users: int = 50_000):
        """P@K, R@K, F1. Only users with >= k test items count toward precision."""
        user_ratings: dict = {}
        for uid, iid, r_ui in testset:
            uid_s = str(uid)
            if uid_s not in user_ratings:
                user_ratings[uid_s] = []
            user_ratings[uid_s].append({
                'actual':    float(r_ui),
                'estimated': self.predict(uid, iid).est,
            })

        prec_list, rec_list = [], []
        for uid_s, ratings in list(user_ratings.items())[:max_users]:
            n_rel = sum(1 for r in ratings if r['actual'] >= threshold)
            top_k = sorted(ratings, key=lambda x: x['estimated'], reverse=True)[:k]
            n_rel_k = sum(
                1 for r in top_k
                if r['actual'] >= threshold and r['estimated'] >= threshold
            )
            if len(ratings) >= k:          # only meaningful precision
                prec_list.append(n_rel_k / k)
            if n_rel:
                rec_list.append(n_rel_k / n_rel)

        p  = float(np.mean(prec_list)) if prec_list else 0.0
        r  = float(np.mean(rec_list))  if rec_list  else 0.0
        f1 = 2 * p * r / (p + r + 1e-8)
        return {
            'Precision@K': round(p, 4),
            'Recall@K':    round(r, 4),
            'F1':          round(f1, 4),
        }


# ---------------------------------------------------------------------------
# Training function
# ---------------------------------------------------------------------------

def train_mf_gpu(ratings_df,
                 n_factors:    int   = 128,
                 n_epochs:     int   = 80,
                 lr:           float = 0.002,
                 weight_decay: float = 0.08,
                 batch_size:   int   = 131_072,
                 dropout:      float = 0.20,
                 patience:     int   = 15,
                 val_frac:     float = 0.10):
    """
    Train NeuralMF on GPU with full VRAM data pre-loading.
    All training tensors live on GPU -- zero CPU-GPU transfer during training.
    Falls back to CPU if CUDA unavailable.
    """
    if not TORCH_AVAILABLE:
        raise ImportError("Install PyTorch: pip install torch")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}  "
              f"({torch.cuda.get_device_properties(0).total_memory // 1024**2} MB VRAM)")
    else:
        print("  No CUDA -- training on CPU")

    # ID encoding
    users = ratings_df['user_id'].astype(str).values
    items = ratings_df['product_id'].astype(str).values
    rates = ratings_df['rating'].astype(np.float32).values

    user_to_idx = {u: i for i, u in enumerate(sorted(set(users)))}
    item_to_idx = {it: i for i, it in enumerate(sorted(set(items)))}
    n_users     = len(user_to_idx)
    n_items     = len(item_to_idx)
    global_mean = float(rates.mean())

    print(f"  {n_users:,} users | {n_items:,} items | "
          f"{len(rates):,} ratings | mean={global_mean:.3f}")

    u_enc = np.fromiter((user_to_idx[u]  for u in users), dtype=np.int64, count=len(users))
    i_enc = np.fromiter((item_to_idx[it] for it in items), dtype=np.int64, count=len(items))
    rates_c = rates - global_mean  # centre around 0

    # Train / val split
    n    = len(rates_c)
    perm = np.random.permutation(n)
    cut  = int((1.0 - val_frac) * n)
    tr_idx, va_idx = perm[:cut], perm[cut:]

    # Pre-load ALL training data to GPU VRAM (~30 MB for 1.5M ratings)
    tr_u = torch.tensor(u_enc[tr_idx],    dtype=torch.long,    device=device)
    tr_i = torch.tensor(i_enc[tr_idx],    dtype=torch.long,    device=device)
    tr_r = torch.tensor(rates_c[tr_idx],  dtype=torch.float32, device=device)
    va_u = torch.tensor(u_enc[va_idx],    dtype=torch.long,    device=device)
    va_i = torch.tensor(i_enc[va_idx],    dtype=torch.long,    device=device)
    va_r = torch.tensor(rates_c[va_idx],  dtype=torch.float32, device=device)
    n_train = len(tr_idx)

    vram_mb = (tr_u.nbytes + tr_i.nbytes + tr_r.nbytes +
               va_u.nbytes + va_i.nbytes + va_r.nbytes) / 1024 / 1024
    print(f"  Training tensors on GPU: {vram_mb:.1f} MB")

    # Model
    model   = _NeuralMF(n_users, n_items, n_factors, dropout).to(device)
    use_amp = device.type == 'cuda'
    scaler  = torch.amp.GradScaler('cuda') if use_amp else None

    # Separate param groups: biases need much less L2 than embeddings
    emb_params  = [*model.user_emb.parameters(), *model.item_emb.parameters()]
    bias_params = [model.global_bias,
                   *model.user_bias.parameters(),
                   *model.item_bias.parameters()]
    mlp_params  = list(model.mlp.parameters())

    optimizer = torch.optim.AdamW([
        {'params': emb_params,  'weight_decay': weight_decay,        'lr': lr},
        {'params': bias_params, 'weight_decay': weight_decay * 0.02, 'lr': lr * 2},
        {'params': mlp_params,  'weight_decay': weight_decay * 0.3,  'lr': lr},
    ])

    # ReduceLROnPlateau: halves LR when val_RMSE plateaus for 4 epochs
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', patience=4, factor=0.5,
        min_lr=lr * 0.02
    )
    mse_fn = nn.MSELoss()

    best_val_rmse = float('inf')
    best_state    = None
    no_improve    = 0

    n_batches_per_epoch = (n_train + batch_size - 1) // batch_size
    print(f"\n  NeuralMF: n_factors={n_factors}  epochs={n_epochs}  "
          f"batch={batch_size:,}  dropout={dropout}  "
          f"batches/epoch={n_batches_per_epoch}  AMP={use_amp}")
    t0 = time.time()

    WARMUP_EPOCHS = 5
    for epoch in range(1, n_epochs + 1):

        # LR warmup
        if epoch <= WARMUP_EPOCHS:
            wf = epoch / WARMUP_EPOCHS
            for pg in optimizer.param_groups:
                pg['lr'] = pg.get('_base_lr', lr) * wf
            if epoch == 1:
                for pg in optimizer.param_groups:
                    pg['_base_lr'] = pg['lr'] / wf if wf > 0 else pg['lr']

        # Shuffle on GPU
        model.train()
        perm_gpu = torch.randperm(n_train, device=device)
        ep_loss  = 0.0

        for start in range(0, n_train, batch_size):
            idx = perm_gpu[start:start + batch_size]
            bu, bi, br = tr_u[idx], tr_i[idx], tr_r[idx]
            optimizer.zero_grad(set_to_none=True)

            if use_amp:
                with torch.amp.autocast('cuda'):
                    pred = model(bu, bi)
                    loss = mse_fn(pred, br)
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                pred = model(bu, bi)
                loss = mse_fn(pred, br)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()

            ep_loss += loss.item()

        # Validate
        model.eval()
        with torch.no_grad():
            if use_amp:
                with torch.amp.autocast('cuda'):
                    vp = model(va_u, va_i)
            else:
                vp = model(va_u, va_i)
            val_rmse = float(torch.sqrt(mse_fn(vp, va_r)).item())

        if epoch > WARMUP_EPOCHS:
            scheduler.step(val_rmse)

        cur_lr = optimizer.param_groups[0]['lr']
        if epoch == 1 or epoch % 5 == 0 or epoch <= WARMUP_EPOCHS:
            print(f"    Epoch {epoch:3d}/{n_epochs}  "
                  f"loss={ep_loss/n_batches_per_epoch:.4f}  "
                  f"val_RMSE={val_rmse:.4f}  lr={cur_lr:.6f}")

        if val_rmse < best_val_rmse - 1e-5:
            best_val_rmse = val_rmse
            best_state    = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve    = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                print(f"    Early stop at epoch {epoch}  "
                      f"best_RMSE={best_val_rmse:.4f}")
                break

    total_time = round(time.time() - t0, 1)
    print(f"\n  Done.  best_val_RMSE={best_val_rmse:.4f}  ({total_time}s)")

    # Extract weights to CPU numpy
    model.load_state_dict(best_state)
    model.eval().cpu()

    with torch.no_grad():
        uf  = model.user_emb.weight.numpy().copy()
        itf = model.item_emb.weight.numpy().copy()
        ub  = model.user_bias.weight.numpy().ravel()
        ib  = model.item_bias.weight.numpy().ravel()
        gb  = float(model.global_bias.numpy())

        # Extract MLP weights for numpy inference
        mlp_weights = []
        mods = list(model.mlp.children())
        j = 0
        while j < len(mods):
            m = mods[j]
            if isinstance(m, nn.Linear):
                W = m.weight.numpy().copy()
                b = m.bias.numpy().copy() if m.bias is not None else np.zeros(m.out_features)
                norm_params = None
                act = None
                j += 1
                if j < len(mods) and isinstance(mods[j], nn.LayerNorm):
                    ln = mods[j]
                    norm_params = (
                        ln.weight.numpy().copy(),
                        ln.bias.numpy().copy(),
                        np.zeros(ln.normalized_shape),
                        np.ones(ln.normalized_shape),
                    )
                    j += 1
                if j < len(mods) and isinstance(mods[j], nn.ReLU):
                    act = 'relu'
                    j += 1
                if j < len(mods) and isinstance(mods[j], nn.Dropout):
                    j += 1  # skip dropout at inference
                mlp_weights.append((W, b, act, norm_params))
            else:
                j += 1

    del model, tr_u, tr_i, tr_r, va_u, va_i, va_r
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Final numpy RMSE on validation (uses global_mean + full MF + MLP)
    wrapper = SurpriseCompatibleMF(
        user_factors=uf, item_factors=itf,
        user_bias=ub, item_bias=ib,
        global_bias=gb,
        user_to_idx=user_to_idx,
        item_to_idx=item_to_idx,
        global_mean=global_mean,
        mlp_weights=mlp_weights,
    )

    CHUNK = 32_768
    preds_val = np.empty(len(va_idx), dtype=np.float32)
    for start in range(0, len(va_idx), CHUNK):
        end = min(start + CHUNK, len(va_idx))
        ui  = u_enc[va_idx[start:end]]
        ii  = i_enc[va_idx[start:end]]
        p_v = (global_mean + gb
               + ub[ui] + ib[ii]
               + np.einsum('ij,ij->i', uf[ui], itf[ii]))
        preds_val[start:end] = np.clip(p_v, 1.0, 5.0)

    r_val = rates[va_idx]
    rmse  = float(np.sqrt(np.mean((preds_val - r_val) ** 2)))
    mae   = float(np.mean(np.abs(preds_val - r_val)))
    print(f"  Validation  RMSE={rmse:.4f}  MAE={mae:.4f}")

    testset = [
        (users[va_idx[j]], items[va_idx[j]], float(rates[va_idx[j]]))
        for j in range(len(va_idx))
    ]

    metrics = {
        'RMSE':          round(rmse, 4),
        'MAE':           round(mae, 4),
        'Training Time': total_time,
        'best_val_RMSE': round(best_val_rmse, 4),
        'n_factors':     n_factors,
        'n_users':       n_users,
        'n_items':       n_items,
    }
    return wrapper, metrics, testset
