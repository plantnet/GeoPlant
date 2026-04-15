"""Species-only PseudoPA baseline with PA masking and joint PA+PO training."""

from .config import JointTrainingConfig
from .data import SpeciesSetDataset, load_metadata_frame, split_frame
from .evaluation import evaluate_completion_from_pa, evaluate_pa_topk, initialize_species_bias_from_pa
from .model import TwoTowerSpeciesModel
from .training import train_joint_model

__all__ = [
    "JointTrainingConfig",
    "SpeciesSetDataset",
    "TwoTowerSpeciesModel",
    "evaluate_completion_from_pa",
    "evaluate_pa_topk",
    "initialize_species_bias_from_pa",
    "load_metadata_frame",
    "split_frame",
    "train_joint_model",
]
