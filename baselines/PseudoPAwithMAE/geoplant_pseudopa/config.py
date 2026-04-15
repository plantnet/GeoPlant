from dataclasses import dataclass


@dataclass
class JointTrainingConfig:
    num_species: int
    embedding_dim: int = 256
    hidden_dim: int = 1024
    dropout: float = 0.1
    mask_ratio: float = 0.4
    pa_negative_ratio: float = 8.0
    po_negative_ratio: float = 4.0
    prevalence_temperature: float = 0.5
    prevalence_floor: float = 1e-6
    lambda_po: float = 1.0
    learning_rate: float = 2e-4
    weight_decay: float = 1e-4
    batch_size: int = 64
    warmup_pa_epochs: int = 5
    joint_epochs: int = 20
    max_po_positives_per_plot: int = 32
