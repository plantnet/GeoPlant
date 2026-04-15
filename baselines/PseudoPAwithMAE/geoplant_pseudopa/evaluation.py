from __future__ import annotations

import random

import torch

from .model import TwoTowerSpeciesModel


@torch.no_grad()
def initialize_species_bias_from_pa(
    model: TwoTowerSpeciesModel,
    loader,
    *,
    device: torch.device,
    prevalence_floor: float = 1e-6,
) -> None:
    positive_counts = torch.zeros(model.num_species, dtype=torch.float64, device=device)
    plot_counts = 0

    model.eval()
    for batch in loader:
        x = batch["x"].to(device).float()
        positive_counts += x.sum(dim=0)
        plot_counts += x.shape[0]

    prevalence = (positive_counts / max(1, plot_counts)).clamp(
        min=prevalence_floor,
        max=1.0 - prevalence_floor,
    )
    logits = torch.log(prevalence / (1.0 - prevalence))
    model.species_bias.weight[:, 0].copy_(logits.float())


@torch.no_grad()
def evaluate_pa_topk(
    model: TwoTowerSpeciesModel,
    loader,
    *,
    device: torch.device,
    ks: tuple[int, ...] = (5, 10, 20),
) -> dict[str, float]:
    model.eval()
    recall_sums = {k: 0.0 for k in ks}
    precision_sums = {k: 0.0 for k in ks}
    total_plots = 0

    for batch in loader:
        x = batch["x"].to(device)
        loc = batch.get("loc")
        if isinstance(loc, torch.Tensor):
            loc = loc.to(device)
        logits = model.score_all_species(x, loc=loc)
        probs = torch.sigmoid(logits)
        top_idx = torch.topk(probs, k=max(ks), dim=1).indices

        total_plots += x.shape[0]
        for k in ks:
            pred_idx = top_idx[:, :k]
            hits = x.gather(1, pred_idx).sum(dim=1)
            true_count = x.sum(dim=1).clamp_min(1.0)
            recall_sums[k] += float((hits / true_count).sum().item())
            precision_sums[k] += float((hits / float(k)).sum().item())

    if total_plots == 0:
        return {f"recall@{k}": 0.0 for k in ks} | {f"precision@{k}": 0.0 for k in ks}

    metrics = {}
    for k in ks:
        metrics[f"recall@{k}"] = recall_sums[k] / total_plots
        metrics[f"precision@{k}"] = precision_sums[k] / total_plots
    return metrics


@torch.no_grad()
def evaluate_completion_from_pa(
    model: TwoTowerSpeciesModel,
    loader,
    *,
    device: torch.device,
    drop_rate: float,
    ks: tuple[int, ...] = (5, 10, 20),
    seed: int = 42,
) -> dict[str, float]:
    model.eval()
    rng = random.Random(seed)
    recall_sums = {k: 0.0 for k in ks}
    precision_sums = {k: 0.0 for k in ks}
    hidden_recall_sums = {k: 0.0 for k in ks}
    richness_error_sum = 0.0
    total_plots = 0

    for batch in loader:
        x_true = batch["x"].to(device)
        loc = batch.get("loc")
        if isinstance(loc, torch.Tensor):
            loc = loc.to(device)
        x_input = x_true.clone()
        batch_size = x_true.shape[0]

        hidden_targets = torch.zeros_like(x_true)
        for row_idx in range(batch_size):
            pos_idx = torch.where(x_true[row_idx] > 0)[0].tolist()
            if len(pos_idx) <= 1:
                continue
            num_hide = max(1, int(round(drop_rate * len(pos_idx))))
            num_hide = min(num_hide, len(pos_idx) - 1)
            hidden_idx = rng.sample(pos_idx, num_hide)
            hidden_targets[row_idx, hidden_idx] = 1.0
            x_input[row_idx, hidden_idx] = 0.0

        logits = model.score_all_species(x_input, loc=loc)
        probs = torch.sigmoid(logits)

        observed_mask = x_input > 0
        probs = probs.masked_fill(observed_mask, float("-inf"))
        top_idx = torch.topk(probs, k=max(ks), dim=1).indices

        total_plots += batch_size
        true_count = x_true.sum(dim=1).clamp_min(1.0)
        hidden_count = hidden_targets.sum(dim=1).clamp_min(1.0)
        predicted_richness = torch.sigmoid(logits.masked_fill(observed_mask, -30.0)).sum(dim=1)
        richness_error_sum += float((predicted_richness - true_count).abs().sum().item())

        for k in ks:
            pred_idx = top_idx[:, :k]
            full_hits = x_true.gather(1, pred_idx).sum(dim=1)
            hidden_hits = hidden_targets.gather(1, pred_idx).sum(dim=1)
            recall_sums[k] += float((full_hits / true_count).sum().item())
            precision_sums[k] += float((full_hits / float(k)).sum().item())
            hidden_recall_sums[k] += float((hidden_hits / hidden_count).sum().item())

    if total_plots == 0:
        return (
            {f"completion_recall@{k}": 0.0 for k in ks}
            | {f"completion_precision@{k}": 0.0 for k in ks}
            | {f"hidden_recall@{k}": 0.0 for k in ks}
            | {"completion_richness_l1": 0.0, "drop_rate": drop_rate}
        )

    metrics = {"drop_rate": drop_rate, "completion_richness_l1": richness_error_sum / total_plots}
    for k in ks:
        metrics[f"completion_recall@{k}"] = recall_sums[k] / total_plots
        metrics[f"completion_precision@{k}"] = precision_sums[k] / total_plots
        metrics[f"hidden_recall@{k}"] = hidden_recall_sums[k] / total_plots
    return metrics


@torch.no_grad()
def evaluate_completion_from_inputs(
    model: TwoTowerSpeciesModel,
    *,
    x_input: torch.Tensor,
    x_true: torch.Tensor,
    input_loc: torch.Tensor | None = None,
    device: torch.device,
    ks: tuple[int, ...] = (5, 10, 20),
) -> dict[str, float]:
    model.eval()
    if x_input.shape != x_true.shape:
        raise ValueError(f"x_input shape {x_input.shape} does not match x_true shape {x_true.shape}")
    if x_input.ndim != 2:
        raise ValueError("x_input and x_true must be rank-2 tensors")

    x_input = x_input.to(device)
    x_true = x_true.to(device)
    if input_loc is not None:
        input_loc = input_loc.to(device)
    logits = model.score_all_species(x_input, loc=input_loc)
    probs = torch.sigmoid(logits)

    observed_mask = x_input > 0
    hidden_targets = (x_true > 0) & (~observed_mask)
    probs = probs.masked_fill(observed_mask, float("-inf"))
    top_idx = torch.topk(probs, k=max(ks), dim=1).indices

    total_plots = x_true.shape[0]
    true_count = x_true.sum(dim=1).clamp_min(1.0)
    hidden_count = hidden_targets.sum(dim=1).clamp_min(1.0)
    predicted_richness = torch.sigmoid(logits.masked_fill(observed_mask, -30.0)).sum(dim=1)
    richness_error = float((predicted_richness - true_count).abs().sum().item()) / max(1, total_plots)

    metrics = {"completion_richness_l1": richness_error}
    for k in ks:
        pred_idx = top_idx[:, :k]
        full_hits = x_true.gather(1, pred_idx).sum(dim=1)
        hidden_hits = hidden_targets.float().gather(1, pred_idx).sum(dim=1)
        metrics[f"completion_recall@{k}"] = float((full_hits / true_count).sum().item()) / max(1, total_plots)
        metrics[f"completion_precision@{k}"] = float((full_hits / float(k)).sum().item()) / max(1, total_plots)
        metrics[f"hidden_recall@{k}"] = float((hidden_hits / hidden_count).sum().item()) / max(1, total_plots)
    return metrics


@torch.no_grad()
def evaluate_location_sdm(
    model: TwoTowerSpeciesModel,
    loader,
    *,
    device: torch.device,
    ks: tuple[int, ...] = (5, 10, 20),
) -> dict[str, float]:
    model.eval()
    recall_sums = {k: 0.0 for k in ks}
    precision_sums = {k: 0.0 for k in ks}
    richness_error_sum = 0.0
    total_plots = 0

    for batch in loader:
        x_true = batch["x"].to(device)
        loc = batch.get("loc")
        if isinstance(loc, torch.Tensor):
            loc = loc.to(device)
        x_input = torch.zeros_like(x_true)
        logits = model.score_all_species(x_input, loc=loc)
        probs = torch.sigmoid(logits)
        top_idx = torch.topk(probs, k=max(ks), dim=1).indices

        total_plots += x_true.shape[0]
        true_count = x_true.sum(dim=1).clamp_min(1.0)
        richness_error_sum += float((probs.sum(dim=1) - true_count).abs().sum().item())

        for k in ks:
            pred_idx = top_idx[:, :k]
            hits = x_true.gather(1, pred_idx).sum(dim=1)
            recall_sums[k] += float((hits / true_count).sum().item())
            precision_sums[k] += float((hits / float(k)).sum().item())

    if total_plots == 0:
        return (
            {f"sdm_recall@{k}": 0.0 for k in ks}
            | {f"sdm_precision@{k}": 0.0 for k in ks}
            | {"sdm_richness_l1": 0.0}
        )

    metrics = {"sdm_richness_l1": richness_error_sum / total_plots}
    for k in ks:
        metrics[f"sdm_recall@{k}"] = recall_sums[k] / total_plots
        metrics[f"sdm_precision@{k}"] = precision_sums[k] / total_plots
    return metrics
