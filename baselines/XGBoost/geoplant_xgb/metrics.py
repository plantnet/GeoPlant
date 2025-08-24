"""Evaluation metrics for multi-label ranking with Top‑K selection."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score


def sample_f1_at_k(y_true_binary: np.ndarray, y_scores: np.ndarray, k: int) -> float:
    """Sample-averaged F1 (Fs1) computed from per-sample Top‑K predictions."""
    n_samples, n_species = y_true_binary.shape
    k = max(1, min(int(k), n_species))
    topk_idx = np.argpartition(-y_scores, kth=k - 1, axis=1)[:, :k]
    y_pred = np.zeros_like(y_true_binary, dtype=np.int32)
    rows = np.arange(n_samples)[:, None]
    y_pred[rows, topk_idx] = 1
    tp = (y_pred & y_true_binary).sum(axis=1)
    fp = (y_pred & (1 - y_true_binary)).sum(axis=1)
    fn = ((1 - y_pred) & y_true_binary).sum(axis=1)
    f1 = tp / (tp + 0.5 * (fp + fn) + 1e-12)
    return float(f1.mean())


def sample_recall_at_k(
    y_true_binary: np.ndarray, y_scores: np.ndarray, k: int
) -> float:
    """Sample-averaged Recall at Top‑K."""
    n_samples, n_species = y_true_binary.shape
    k = max(1, min(int(k), n_species))
    topk_idx = np.argpartition(-y_scores, kth=k - 1, axis=1)[:, :k]
    y_pred = np.zeros_like(y_true_binary, dtype=np.int32)
    rows = np.arange(n_samples)[:, None]
    y_pred[rows, topk_idx] = 1
    tp = (y_pred & y_true_binary).sum(axis=1)
    positives = y_true_binary.sum(axis=1).clip(min=1)
    return float((tp / positives).mean())


def macro_auc(y_true_binary: np.ndarray, y_scores: np.ndarray) -> float:
    """Macro-average ROC‑AUC across species with both classes present."""
    aucs = []
    for j in range(y_true_binary.shape[1]):
        yj = y_true_binary[:, j]
        if len(np.unique(yj)) < 2:
            continue
        aucs.append(roc_auc_score(yj, y_scores[:, j]))
    return float(np.mean(aucs)) if aucs else float("nan")
