-- IntelliRec — cart_items table + RLS
-- Run in Supabase SQL Editor.
--
-- Mirrors the existing public.wishlist schema so the cart behaves the same
-- way (per-user rows, on-conflict updates).  The denormalised product_title
-- / product_price / product_category columns are intentional: they let the
-- cart render even if the recommendation engine is mid-restart, without a
-- second query against products_df.
--
-- RLS is enforced so a user can ONLY read/write their own rows.  The
-- profiles / wishlist / user_preferences / recommendation_history /
-- feedback policies are left untouched — this migration only adds
-- cart_items.

create table if not exists public.cart_items (
    id                 uuid        not null default gen_random_uuid() primary key,
    user_id            uuid        not null references auth.users(id) on delete cascade,
    product_id         text        not null,
    product_title      text,
    product_price      numeric(12,2) default 0,
    product_category   text,
    quantity           integer     not null default 1 check (quantity > 0),
    added_at           timestamptz not null default now(),
    updated_at         timestamptz not null default now(),
    unique (user_id, product_id)
);

create index if not exists cart_items_user_id_idx on public.cart_items(user_id);

alter table public.cart_items enable row level security;

drop policy if exists "cart_items: own rows select" on public.cart_items;
create policy "cart_items: own rows select"
    on public.cart_items for select
    using (auth.uid() = user_id);

drop policy if exists "cart_items: own rows insert" on public.cart_items;
create policy "cart_items: own rows insert"
    on public.cart_items for insert
    with check (auth.uid() = user_id);

drop policy if exists "cart_items: own rows update" on public.cart_items;
create policy "cart_items: own rows update"
    on public.cart_items for update
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

drop policy if exists "cart_items: own rows delete" on public.cart_items;
create policy "cart_items: own rows delete"
    on public.cart_items for delete
    using (auth.uid() = user_id);

-- Keep updated_at fresh on every UPDATE (needed because the API does
-- upsert with on_conflict='user_id,product_id', which becomes UPDATE on
-- conflict).
create or replace function public.set_cart_items_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

drop trigger if exists trg_cart_items_updated_at on public.cart_items;
create trigger trg_cart_items_updated_at
    before update on public.cart_items
    for each row execute function public.set_cart_items_updated_at();
