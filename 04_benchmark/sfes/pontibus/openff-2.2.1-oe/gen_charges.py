from pathlib import Path
import pandas
from openff.toolkit import (
    Molecule,
    OpenEyeToolkitWrapper,
    AmberToolsToolkitWrapper,
    RDKitToolkitWrapper,
)
from openff.toolkit.utils.nagl_wrapper import NAGLToolkitWrapper
from openff.toolkit.utils.base_wrapper import ToolkitWrapper
from rdkit.Chem.rdmolfiles import SDWriter
from typing import Iterable
from tqdm import tqdm


def slugify(s: str) -> str:
    return "-".join(s.lower().split())

def charge_and_write_sdf(
    all_smiles: Iterable[str],
    partial_charge_method: str,
    toolkit_registry: ToolkitWrapper,
):
    path = Path(f"all_molecules_{partial_charge_method}_{slugify(toolkit_registry._toolkit_name)}.sdf")
    if path.exists():
        print(path, "already exists; skipping")
        return
    writer = SDWriter(path)
    for smiles in tqdm(all_smiles):
        mol = Molecule.from_smiles(smiles)
        mol.assign_partial_charges(
            partial_charge_method,
            toolkit_registry=toolkit_registry,
        )
        mol.generate_conformers(
            n_conformers=1,
            toolkit_registry=RDKitToolkitWrapper(),
        )
        mol.properties["SMILES"] = smiles
        writer.write(mol.to_rdkit())


def run():
    fsolv_data = pandas.read_csv("sage-fsolv-test-v1.csv")
    mnsol_data = pandas.read_csv("sage-mnsol-test-v1.txt")

    # Don't generate charges for water because it should be TIP3
    assert all(fsolv_data["Role 1"] == "Solvent")
    assert all(fsolv_data["Component 1"] == "O")

    # Get all the molecules in either dataset (except water)
    all_smiles = list(set(
        [
            *fsolv_data["Component 2"],
            *mnsol_data["Component 1"],
            *mnsol_data["Component 2"],
        ]
    ))

    assert "O" not in all_smiles

    # Generate charges with OpenEye and write to SDF file
    charge_and_write_sdf(
        all_smiles=all_smiles,
        partial_charge_method="am1bccelf10",
        toolkit_registry=OpenEyeToolkitWrapper(),
    )

    # Generate charges with AmberTools and write to SDF file
    charge_and_write_sdf(
        all_smiles=all_smiles,
        partial_charge_method="am1bcc",
        toolkit_registry=AmberToolsToolkitWrapper(),
    )

    # Generate charges with NAGL and write to SDF file
    charge_and_write_sdf(
        all_smiles=all_smiles,
        partial_charge_method="openff-gnn-am1bcc-0.1.0-rc.3.pt",
        toolkit_registry=NAGLToolkitWrapper(),
    )



if __name__ == "__main__":
    run()
