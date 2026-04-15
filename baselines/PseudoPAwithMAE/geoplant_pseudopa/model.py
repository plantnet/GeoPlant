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
        use_location: bool = False,
        location_dim: int = 2,
        location_hidden_dim: int = 64,
    ) -> None:
        super().__init__()
        self.num_species = num_species
        self.use_location = use_location
        self.species_plot_encoder = nn.Sequential(
            nn.Linear(num_species, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embedding_dim),
            nn.ReLU(),
        )
        self.location_encoder = None
        if use_location:
            self.location_encoder = nn.Sequential(
                nn.Linear(location_dim, location_hidden_dim),
                nn.ReLU(),
                nn.Linear(location_hidden_dim, embedding_dim),
            )
        self.species_embedding = nn.Embedding(num_species, embedding_dim)
        self.species_bias = nn.Embedding(num_species, 1)
        nn.init.xavier_uniform_(self.species_embedding.weight)
        nn.init.zeros_(self.species_bias.weight)

    def encode_plot(self, x: torch.Tensor, loc: torch.Tensor | None = None) -> torch.Tensor:
        species_embedding = self.species_plot_encoder(x)
        if self.use_location and self.location_encoder is not None and loc is not None:
            return species_embedding + self.location_encoder(loc.float())
        return species_embedding

    def score_indices(self, plot_embedding: torch.Tensor, species_idx: torch.Tensor) -> torch.Tensor:
        plot_embedding32 = plot_embedding.float()
        species_embedding32 = self.species_embedding(species_idx).float()
        species_bias32 = self.species_bias(species_idx).squeeze(-1).float()
        logits = plot_embedding32 @ species_embedding32.t() + species_bias32
        return logits.to(plot_embedding.dtype)

    def score_all_species(self, x: torch.Tensor, loc: torch.Tensor | None = None) -> torch.Tensor:
        plot_embedding = self.encode_plot(x, loc=loc)
        plot_embedding32 = plot_embedding.float()
        species_embedding32 = self.species_embedding.weight.float()
        species_bias32 = self.species_bias.weight.squeeze(-1).float()
        logits = plot_embedding32 @ species_embedding32.t() + species_bias32
        return logits.to(plot_embedding.dtype)
