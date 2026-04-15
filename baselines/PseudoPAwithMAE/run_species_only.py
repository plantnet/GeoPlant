from __future__ import annotations

import argparse

from torch.utils.data import DataLoader

from geoplant_pseudopa import (
    JointTrainingConfig,
    SpeciesSetDataset,
    load_metadata_frame,
    split_frame,
    train_joint_model,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train the species-only PseudoPA baseline with PA masking and joint PA+PO learning."
    )
    parser.add_argument("--train-metadata", required=True, help="CSV with species_set, source, and subset columns")
    parser.add_argument("--val-metadata", required=True, help="CSV with species_set, source, and subset columns")
    parser.add_argument("--num-species", required=True, type=int)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--warmup-pa-epochs", type=int, default=5)
    parser.add_argument("--joint-epochs", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    train_frame = load_metadata_frame(args.train_metadata)
    val_frame = load_metadata_frame(args.val_metadata)

    pa_train_dataset = SpeciesSetDataset(
        split_frame(train_frame, source="PA", subset="train"),
        args.num_species,
    )
    po_train_dataset = SpeciesSetDataset(
        split_frame(train_frame, source="PO", subset="train"),
        args.num_species,
    )
    val_dataset = SpeciesSetDataset(
        split_frame(val_frame, source="PA", subset="val"),
        args.num_species,
    )

    pa_train_loader = DataLoader(pa_train_dataset, batch_size=args.batch_size, shuffle=True)
    po_train_loader = DataLoader(po_train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

    config = JointTrainingConfig(
        num_species=args.num_species,
        batch_size=args.batch_size,
        warmup_pa_epochs=args.warmup_pa_epochs,
        joint_epochs=args.joint_epochs,
    )
    _, history = train_joint_model(
        pa_train_loader,
        po_train_loader,
        val_loader,
        config=config,
        device=args.device,
    )

    for row in history:
        print(row)


if __name__ == "__main__":
    main()
