from pathlib import Path
from typing import Iterable, Iterator

from openff.toolkit import (
    Molecule,
    RDKitToolkitWrapper,
)
from openff.toolkit.utils.base_wrapper import ToolkitWrapper
from openff.toolkit.utils.nagl_wrapper import NAGLToolkitWrapper
from rdkit import Chem
from rdkit.Chem.rdmolfiles import SDWriter
from tqdm import tqdm


def slugify(s: str) -> str:
    return "-".join(s.lower().split())


def charge_and_write_sdf(
    all_molecules: Iterable[Molecule],
    partial_charge_method: str,
    toolkit_registry: ToolkitWrapper,
    prefix: str = "all_molecules",
    skip_smiles: Iterable = (),
):
    path = Path(
        f"{prefix}_{partial_charge_method}_{slugify(toolkit_registry._toolkit_name)}.sdf"
    )
    if path.exists():
        print(path, "already exists; skipping")
        return
    writer = SDWriter(path)
    for mol in tqdm(all_molecules):
        assert "SMILES" in mol.properties or "mapped_smiles" in mol.properties
        smiles = mol.properties.get("SMILES", None) or mol.properties.get("mapped_smiles", None)
        if smiles in skip_smiles:
            continue
        print(mol.to_smiles(), mol.properties.get("SMILES", None), mol.properties.get("mapped_smiles", None))
        mol.assign_partial_charges(
            partial_charge_method,
            toolkit_registry=toolkit_registry,
        )
        if mol.n_atoms > 3 and all(z == 0.0 for _, _, z in mol.conformers[0]):
            mol.generate_conformers(n_conformers=1)
        writer.write(mol.to_rdkit())


def sdf_to_openff(filename: str) -> Iterator[Molecule]:
    print(filename)
    for rdmol in Chem.SDMolSupplier(filename, removeHs=False):
        yield Molecule.from_rdkit(rdmol, allow_undefined_stereo=True)


def run():
    # Generate charges with NAGL and write to SDF file
    charge_and_write_sdf(
        all_molecules=[
            *sdf_to_openff(
                "../openff-2.2.1-oe/all_molecules_openff-gnn-am1bcc-0.1.0-rc.3.pt_openff-nagl.sdf"
            ),
            *sdf_to_openff("../openff-2.2.1-oe/highrmse-molecules-openeye.sdf"),
        ],
        partial_charge_method="openff-gnn-am1bcc-0.1.0-rc.3.pt",
        toolkit_registry=NAGLToolkitWrapper(),
        prefix="mnsol_freesolv_highrmse",
        skip_smiles={
            "[H:1][C:2]([H:3])([H:4])[S:5]([C:6]([H:7])([H:8])[H:9])([C:10]([H:11])([H:12])[C:13]([H:14])([H:15])[O:16][H:17])[I:18]",
            "[S:1]([S:2][Br:3])[Br:4]",
        },
    )


if __name__ == "__main__":
    run()
