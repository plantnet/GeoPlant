from __future__ import annotations

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
        logits = model.score_all_species(x)
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
