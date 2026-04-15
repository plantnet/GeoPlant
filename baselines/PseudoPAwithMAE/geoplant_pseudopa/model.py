from __future__ import annotations

import torch
import torch.nn as nn


class TwoTowerSpeciesModel(nn.Module):
    def __init__(
        self,
        num_species: int,
        embedding_dim: int = 256,
        hidden_dim: int = 1024,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.num_species = num_species
        self.plot_encoder = nn.Sequential(
            nn.Linear(num_species, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embedding_dim),
            nn.ReLU(),
        )
        self.species_embedding = nn.Embedding(num_species, embedding_dim)
        self.species_bias = nn.Embedding(num_species, 1)
        nn.init.xavier_uniform_(self.species_embedding.weight)
        nn.init.zeros_(self.species_bias.weight)

    def encode_plot(self, x: torch.Tensor) -> torch.Tensor:
        return self.plot_encoder(x)

    def score_indices(self, plot_embedding: torch.Tensor, species_idx: torch.Tensor) -> torch.Tensor:
        plot_embedding32 = plot_embedding.float()
        species_embedding32 = self.species_embedding(species_idx).float()
        species_bias32 = self.species_bias(species_idx).squeeze(-1).float()
        logits = plot_embedding32 @ species_embedding32.t() + species_bias32
        return logits.to(plot_embedding.dtype)

    def score_all_species(self, x: torch.Tensor) -> torch.Tensor:
        plot_embedding = self.encode_plot(x)
        plot_embedding32 = plot_embedding.float()
        species_embedding32 = self.species_embedding.weight.float()
        species_bias32 = self.species_bias.weight.squeeze(-1).float()
        logits = plot_embedding32 @ species_embedding32.t() + species_bias32
        return logits.to(plot_embedding.dtype)
