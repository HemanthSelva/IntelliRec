"""
utils/diagnostics.py — IntelliRec runtime diagnostics

Single source-of-truth structured logger. Used to instrument the model-loading
path so the difference between local (3000+ products) and Streamlit Cloud
(42-product fallback) is visible in the Manage app → Logs panel.

All output goes to stdout, which Streamlit Cloud captures.
"""
from __future__ import annotations

import hashlib
import logging
import os
import pickle
import sys
import traceback
from typing import Any

try:
    import psutil  # optional
    _HAS_PSUTIL = True
except Exception:
    _HAS_PSUTIL = False


_LOGGER_NAME = "intellirec.diagnostics"


def _build_logger() -> logging.Logger:
    log = logging.getLogger(_LOGGER_NAME)
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    log.addHandler(handler)
    log.propagate = False
    return log


log = _build_logger()


def info(msg: str) -> None:
    log.info(msg)


def warn(msg: str) -> None:
    log.warning(msg)


def error(msg: str) -> None:
    log.error(msg)


def free_mem_mb() -> float:
    if not _HAS_PSUTIL:
        return -1.0
    try:
        return psutil.virtual_memory().available / 1024 / 1024
    except Exception:
        return -1.0


def diagnose_artifact(label: str, path: str, *, do_load: bool = True) -> Any:
    """Log filesystem + load characteristics of a pickle artifact.

    Returns the loaded object (or None on failure / when do_load=False).
    Failures are logged with full traceback but never re-raised — diagnostics
    must not break the caller.
    """
    log.info(f"=== ARTIFACT: {label} ===")
    log.info(f"  cwd            : {os.getcwd()}")
    log.info(f"  abs_path       : {os.path.abspath(path)}")
    exists = os.path.exists(path)
    log.info(f"  exists         : {exists}")
    if not exists:
        log.info(f"  free_mem_MB    : {free_mem_mb():.0f}")
        return None

    try:
        size = os.path.getsize(path)
        log.info(f"  size_MB        : {size / 1024 / 1024:.2f}")
        with open(path, "rb") as f:
            head = f.read(8 * 1024 * 1024)  # bound md5 cost on huge files
            log.info(f"  md5_first8MB   : {hashlib.md5(head).hexdigest()}")
    except Exception as e:
        log.error(f"  stat/md5 failed: {e}")

    log.info(f"  free_mem_MB    : {free_mem_mb():.0f}")

    if not do_load:
        return None

    try:
        with open(path, "rb") as f:
            obj = pickle.load(f)
    except Exception:
        log.error(f"  LOAD FAILED:\n{traceback.format_exc()}")
        return None

    log.info(f"  type           : {type(obj).__name__}")
    for attr in ("shape", "__len__", "columns"):
        try:
            if attr == "__len__" and hasattr(obj, attr):
                log.info(f"  len            : {len(obj)}")
            elif attr == "columns" and hasattr(obj, attr):
                log.info(f"  columns        : {list(obj.columns)}")
            elif attr == "shape" and hasattr(obj, attr):
                log.info(f"  shape          : {obj.shape}")
        except Exception:
            pass
    return obj
