from __future__ import annotations

from dataclasses import asdict
from itertools import cycle

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from .config import JointTrainingConfig
from .evaluation import evaluate_pa_topk, initialize_species_bias_from_pa
from .model import TwoTowerSpeciesModel


def build_frequency_weights(x: torch.Tensor, temperature: float, floor: float) -> torch.Tensor:
    prevalence = x.mean(dim=0).clamp(min=floor)
    weights = prevalence.pow(temperature)
    weights = weights / weights.sum().clamp_min(floor)
    return weights


def sample_negative_indices(
    excluded_idx: torch.Tensor,
    num_species: int,
    count: int,
    *,
    device: torch.device,
    prevalence_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    if count <= 0:
        return torch.empty(0, dtype=torch.long, device=device)

    mask = torch.ones(num_species, dtype=torch.bool, device=device)
    if excluded_idx.numel() > 0:
        mask[excluded_idx] = False

    candidate_idx = torch.where(mask)[0]
    if candidate_idx.numel() == 0:
        return candidate_idx

    count = min(count, int(candidate_idx.numel()))
    if prevalence_weights is None:
        perm = torch.randperm(candidate_idx.numel(), device=device)[:count]
        return candidate_idx[perm]

    candidate_weights = prevalence_weights.index_select(0, candidate_idx)
    candidate_weights = candidate_weights / candidate_weights.sum().clamp_min(1e-12)
    chosen = torch.multinomial(candidate_weights, count, replacement=False)
    return candidate_idx[chosen]


def masked_pa_loss(
    model: TwoTowerSpeciesModel,
    x: torch.Tensor,
    *,
    mask_ratio: float,
    negative_ratio: float,
    prevalence_weights: torch.Tensor | None = None,
) -> tuple[torch.Tensor, float]:
    batch_size, num_species = x.shape
    device = x.device

    batch_losses = []
    batch_mask_fraction = []

    for row_idx in range(batch_size):
        pos_idx = torch.where(x[row_idx] > 0)[0]
        if pos_idx.numel() == 0:
            continue

        num_masked = max(1, int(round(mask_ratio * pos_idx.numel())))
        chosen = torch.randperm(pos_idx.numel(), device=device)[:num_masked]
        masked_idx = pos_idx[chosen]
        masked_input = x[row_idx : row_idx + 1].clone()
        masked_input[0, masked_idx] = 0.0

        num_negatives = max(1, int(round(negative_ratio * masked_idx.numel())))
        neg_idx = sample_negative_indices(
            pos_idx,
            num_species,
            num_negatives,
            device=device,
            prevalence_weights=prevalence_weights,
        )

        eval_idx = torch.cat([masked_idx, neg_idx], dim=0)
        targets = torch.cat(
            [
                torch.ones(masked_idx.numel(), device=device),
                torch.zeros(neg_idx.numel(), device=device),
            ]
        )
        logits = model.score_indices(model.encode_plot(masked_input), eval_idx).squeeze(0)
        batch_losses.append(F.binary_cross_entropy_with_logits(logits.float(), targets.float()))
        batch_mask_fraction.append(masked_idx.numel() / pos_idx.numel())

    if not batch_losses:
        zero = x.new_zeros(())
        return zero, 0.0

    return torch.stack(batch_losses).mean(), float(sum(batch_mask_fraction) / len(batch_mask_fraction))


def po_ranking_loss(
    model: TwoTowerSpeciesModel,
    x: torch.Tensor,
    *,
    negative_ratio: float,
    max_positives_per_plot: int,
    prevalence_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    batch_size, num_species = x.shape
    device = x.device
    plot_embeddings = model.encode_plot(x)
    losses = []

    for row_idx in range(batch_size):
        pos_idx = torch.where(x[row_idx] > 0)[0]
        if pos_idx.numel() == 0:
            continue

        if pos_idx.numel() > max_positives_per_plot:
            chosen = torch.randperm(pos_idx.numel(), device=device)[:max_positives_per_plot]
            pos_idx = pos_idx[chosen]

        num_negatives = max(1, int(round(negative_ratio * pos_idx.numel())))
        neg_idx = sample_negative_indices(
            pos_idx,
            num_species,
            num_negatives,
            device=device,
            prevalence_weights=prevalence_weights,
        )
        if neg_idx.numel() == 0:
            continue

        pos_scores = model.score_indices(plot_embeddings[row_idx : row_idx + 1], pos_idx).squeeze(0)
        neg_scores = model.score_indices(plot_embeddings[row_idx : row_idx + 1], neg_idx).squeeze(0)
        margin = pos_scores.unsqueeze(1) - neg_scores.unsqueeze(0)
        losses.append(-F.logsigmoid(margin).mean())

    if not losses:
        return x.new_zeros(())
    return torch.stack(losses).mean()


def run_epoch(
    model: TwoTowerSpeciesModel,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    *,
    mode: str,
    config: JointTrainingConfig,
    device: torch.device,
) -> dict[str, float]:
    model.train()
    total_pa_loss = 0.0
    total_po_loss = 0.0
    total_examples = 0
    total_mask_fraction = 0.0

    progress = tqdm(loader, desc=f"{mode.upper()} train", leave=False)
    for batch in progress:
        x = batch["x"].to(device)
        prevalence_weights = build_frequency_weights(
            x,
            temperature=config.prevalence_temperature,
            floor=config.prevalence_floor,
        )

        pa_loss, mask_fraction = masked_pa_loss(
            model,
            x,
            mask_ratio=config.mask_ratio,
            negative_ratio=config.pa_negative_ratio,
            prevalence_weights=prevalence_weights,
        )

        po_loss = x.new_zeros(())
        if mode == "joint":
            po_loss = po_ranking_loss(
                model,
                x,
                negative_ratio=config.po_negative_ratio,
                max_positives_per_plot=config.max_po_positives_per_plot,
                prevalence_weights=prevalence_weights,
            )

        loss = pa_loss + config.lambda_po * po_loss

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        batch_size = x.shape[0]
        total_examples += batch_size
        total_pa_loss += float(pa_loss.item()) * batch_size
        total_po_loss += float(po_loss.item()) * batch_size
        total_mask_fraction += mask_fraction * batch_size
        progress.set_postfix(
            pa_loss=f"{float(pa_loss.item()):.4f}",
            po_loss=f"{float(po_loss.item()):.4f}",
            mask=f"{mask_fraction:.3f}",
        )

    if total_examples == 0:
        return {"pa_loss": 0.0, "po_loss": 0.0, "mask_fraction": 0.0}

    return {
        "pa_loss": total_pa_loss / total_examples,
        "po_loss": total_po_loss / total_examples,
        "mask_fraction": total_mask_fraction / total_examples,
    }


def train_joint_model(
    pa_train_loader: DataLoader,
    po_train_loader: DataLoader,
    val_loader: DataLoader,
    *,
    config: JointTrainingConfig,
    device: str = "cpu",
) -> tuple[TwoTowerSpeciesModel, list[dict[str, float]]]:
    device_obj = torch.device(device)
    model = TwoTowerSpeciesModel(
        config.num_species,
        embedding_dim=config.embedding_dim,
        hidden_dim=config.hidden_dim,
        dropout=config.dropout,
    ).to(device_obj)

    with torch.no_grad():
        initialize_species_bias_from_pa(
            model,
            pa_train_loader,
            device=device_obj,
            prevalence_floor=config.prevalence_floor,
        )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )

    history: list[dict[str, float]] = []
    print(
        "Starting training with",
        {
            "device": str(device_obj),
            "warmup_pa_epochs": config.warmup_pa_epochs,
            "joint_epochs": config.joint_epochs,
            "pa_train_plots": len(pa_train_loader.dataset),
            "po_train_plots": len(po_train_loader.dataset),
            "val_plots": len(val_loader.dataset),
            "batch_size": config.batch_size,
        },
    )
    for epoch in range(config.warmup_pa_epochs):
        print(f"[Warmup {epoch + 1}/{config.warmup_pa_epochs}]")
        train_metrics = run_epoch(
            model,
            pa_train_loader,
            optimizer,
            mode="pa",
            config=config,
            device=device_obj,
        )
        val_metrics = evaluate_pa_topk(model, val_loader, device=device_obj)
        history.append(
            {
                "epoch": float(epoch + 1),
                "stage": 0.0,
                **train_metrics,
                **val_metrics,
            }
        )
        print(
            "  train:",
            {
                "pa_loss": round(train_metrics["pa_loss"], 4),
                "po_loss": round(train_metrics["po_loss"], 4),
                "mask_fraction": round(train_metrics["mask_fraction"], 4),
            },
        )
        print("  val:", {key: round(value, 4) for key, value in val_metrics.items()})

    for epoch in range(config.joint_epochs):
        print(f"[Joint {epoch + 1}/{config.joint_epochs}]")
        train_metrics = run_joint_epoch(
            model,
            pa_train_loader,
            po_train_loader,
            optimizer,
            config=config,
            device=device_obj,
        )
        val_metrics = evaluate_pa_topk(model, val_loader, device=device_obj)
        history.append(
            {
                "epoch": float(config.warmup_pa_epochs + epoch + 1),
                "stage": 1.0,
                **train_metrics,
                **val_metrics,
            }
        )
        print(
            "  train:",
            {
                "pa_loss": round(train_metrics["pa_loss"], 4),
                "po_loss": round(train_metrics["po_loss"], 4),
                "mask_fraction": round(train_metrics["mask_fraction"], 4),
            },
        )
        print("  val:", {key: round(value, 4) for key, value in val_metrics.items()})

    model.training_summary = {
        "config": asdict(config),
        "history": history,
    }
    return model, history


def run_joint_epoch(
    model: TwoTowerSpeciesModel,
    pa_loader: DataLoader,
    po_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    *,
    config: JointTrainingConfig,
    device: torch.device,
) -> dict[str, float]:
    model.train()
    total_pa_loss = 0.0
    total_po_loss = 0.0
    total_mask_fraction = 0.0
    total_examples = 0

    if len(pa_loader) == 0:
        return {"pa_loss": 0.0, "po_loss": 0.0, "mask_fraction": 0.0}

    po_iterator = cycle(po_loader) if len(po_loader) > 0 else None

    progress = tqdm(pa_loader, desc="JOINT train", leave=False)
    for pa_batch in progress:
        x_pa = pa_batch["x"].to(device)
        pa_weights = build_frequency_weights(
            x_pa,
            temperature=config.prevalence_temperature,
            floor=config.prevalence_floor,
        )
        pa_loss, mask_fraction = masked_pa_loss(
            model,
            x_pa,
            mask_ratio=config.mask_ratio,
            negative_ratio=config.pa_negative_ratio,
            prevalence_weights=pa_weights,
        )

        po_loss = x_pa.new_zeros(())
        po_batch_size = 0
        if po_iterator is not None:
            po_batch = next(po_iterator)
            x_po = po_batch["x"].to(device)
            po_batch_size = x_po.shape[0]
            po_weights = build_frequency_weights(
                x_po,
                temperature=config.prevalence_temperature,
                floor=config.prevalence_floor,
            )
            po_loss = po_ranking_loss(
                model,
                x_po,
                negative_ratio=config.po_negative_ratio,
                max_positives_per_plot=config.max_po_positives_per_plot,
                prevalence_weights=po_weights,
            )

        loss = pa_loss + config.lambda_po * po_loss
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        pa_batch_size = x_pa.shape[0]
        total_examples += pa_batch_size + po_batch_size
        total_pa_loss += float(pa_loss.item()) * pa_batch_size
        total_po_loss += float(po_loss.item()) * max(1, po_batch_size)
        total_mask_fraction += mask_fraction * pa_batch_size
        progress.set_postfix(
            pa_loss=f"{float(pa_loss.item()):.4f}",
            po_loss=f"{float(po_loss.item()):.4f}",
            mask=f"{mask_fraction:.3f}",
            po_batch=po_batch_size,
        )

    if total_examples == 0:
        return {"pa_loss": 0.0, "po_loss": 0.0, "mask_fraction": 0.0}

    return {
        "pa_loss": total_pa_loss / max(1, len(pa_loader.dataset)),
        "po_loss": total_po_loss / max(1, total_examples),
        "mask_fraction": total_mask_fraction / max(1, len(pa_loader.dataset)),
    }
