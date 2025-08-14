import pathlib
import logging
import typing
import click
import tqdm
import time

from click_option_group import optgroup

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds
import pyarrow.parquet as pq

import openmm
import openmm.app
import openmm.unit
from openff.units import unit
from openff.toolkit import Molecule, ForceField

logger = logging.getLogger(__name__)
#logging.basicConfig(
#    level=logging.INFO,
#    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#)


def optimize_single(
    row,
    forcefield: ForceField,
    ff_name: str,
):
    mol = Molecule.from_mapped_smiles(
        row["mapped_smiles"],
        allow_undefined_stereo=True
    )
    positions = np.array(row["coordinates"]).reshape((-1, 3))
    try:
        system = forcefield.create_interchange(mol.to_topology()).to_openmm(
            combine_nonbonded_forces=False,
        )
    except Exception as e:
        logger.warning(f"Skipping record {row['qcarchive_id']}: {e}")
        return None
    
    context = openmm.Context(
        system,
        openmm.VerletIntegrator(0.1 * openmm.unit.femtoseconds),
        openmm.Platform.getPlatformByName("Reference"),
    )

    context.setPositions(
        (positions * openmm.unit.angstrom).in_units_of(openmm.unit.nanometer),
    )
    openmm.LocalEnergyMinimizer.minimize(
        context=context,
        tolerance=10,
        maxIterations=0,
    )
    state = context.getState(getPositions=True, getEnergy=True)
    coordinates = state.getPositions(asNumpy=True).value_in_unit(openmm.unit.angstrom)
    energy = state.getPotentialEnergy().value_in_unit(openmm.unit.kilocalorie_per_mole)

    return {
        "qcarchive_id": row["qcarchive_id"],
        "cmiles": row["cmiles"],
        "mapped_smiles": row["mapped_smiles"],
        "coordinates": coordinates.flatten().tolist(),
        "energy": energy,
        "method": ff_name,
        "dataset": row["dataset"],
    }


def batch_optimize(
    qcarchive_ids: list[str],
    qm_directory: str,
    forcefield_path: str,
):
    dataset = ds.dataset(qm_directory)
    subset = dataset.filter(
        pc.field("qcarchive_id").isin(qcarchive_ids)
    )
    forcefield = ForceField(forcefield_path)
    ff_name = pathlib.Path(forcefield_path).stem
    rows = subset.to_table().to_pylist()

    entries = []
    for row in tqdm.tqdm(rows):
        entry = optimize_single(row, forcefield, ff_name)
        if entry is not None:
            entries.append(entry)
    return entries



@click.command()
@click.option(
    "--forcefield",
    "-ff",
    "forcefield",
    default="openff_unconstrained-2.2.1.offxml",
    help="Force field to use for labeling",
)
@click.option(
    "--data",
    "-d",
    "data_directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default="data",
    help="Directory containing data files",
)
@optgroup.group("Parallelization configuration")
@optgroup.option(
    "--n-workers",
    help="The number of workers to distribute the labelling across. Use -1 to request "
    "one worker per batch.",
    type=int,
    default=1,
    show_default=True,
)
@optgroup.option(
    "--worker-type",
    help="The type of worker to distribute the labelling across.",
    type=click.Choice(["lsf", "local", "slurm"]),
    default="local",
    show_default=True,
)
@optgroup.option(
    "--batch-size",
    help="The number of molecules to processes at once on a particular worker.",
    type=int,
    default=500,
    show_default=True,
)
@optgroup.group("Cluster configuration", help="Options to configure cluster workers.")
@optgroup.option(
    "--memory",
    help="The amount of memory (GB) to request per queue worker.",
    type=int,
    default=3,
    show_default=True,
)
@optgroup.option(
    "--walltime",
    help="The maximum wall-clock hours to request per queue worker.",
    type=int,
    default=2,
    show_default=True,
)
@optgroup.option(
    "--queue",
    help="The SLURM queue to submit workers to.",
    type=str,
    default="cpuqueue",
    show_default=True,
)
@optgroup.option(
    "--conda-environment",
    help="The conda environment that SLURM workers should run using.",
    type=str,
)
def main(
    forcefield: str = "openff_unconstrained-2.2.1.offxml",
    data_directory: str = "data",
    worker_type: typing.Literal["slurm", "local"] = "local",
    queue: str = "free",
    conda_environment: str = "ib-dev",
    memory: int = 4,  # GB
    walltime: int = 32,  # hours
    batch_size: int = 300,
    n_workers: int = -1,
):
    from openff.nagl.utils._parallelization import batch_distributed
    from dask import distributed

    print(f"{time.ctime()} - Starting batch optimization")
    start_time = time.time()

    data_directory = pathlib.Path(data_directory)
    input_directory = data_directory / "qm"
    input_dataset = ds.dataset(input_directory)
    print(f"Loaded {input_dataset.count_rows()} rows from {input_directory}")
    
    input_qcarchive_ids = input_dataset.to_table(
        columns=["qcarchive_id"]
    ).to_pydict()["qcarchive_id"]
    input_qcarchive_ids = set(input_qcarchive_ids)

    ff_name = pathlib.Path(forcefield).stem
    output_directory = data_directory / ff_name
    output_directory.mkdir(parents=True, exist_ok=True)
    output_dataset = ds.dataset(output_directory)
    n_files = 0
    if output_dataset.count_rows():
        existing_qcarchive_ids = output_dataset.to_table(
            columns=["qcarchive_id"]
        ).to_pydict()["qcarchive_id"]
        print(f"Loaded {len(existing_qcarchive_ids)} rows from {output_directory}")
        input_qcarchive_ids -= set(existing_qcarchive_ids)
        print(f"Filtered to {len(input_qcarchive_ids)} new rows to process")
        n_files  = len(output_dataset.files)

    input_qcarchive_ids = sorted(input_qcarchive_ids)

    with batch_distributed(
        input_qcarchive_ids,
        batch_size=batch_size,
        worker_type=worker_type,
        queue=queue,
        conda_environment=conda_environment,
        memory=memory,
        walltime=walltime,
        n_workers=n_workers,
    ) as batcher:
        futures = list(batcher(
            batch_optimize,
            forcefield_path=forcefield,
            qm_directory=str(input_directory.resolve()),
        ))
        for future in tqdm.tqdm(
            distributed.as_completed(futures, raise_errors=False),
            total=len(futures),
            desc="Optimizing batches",
        ):
            entries = future.result()
            table = pa.Table.from_pylist(entries)
            table_file = output_directory / f"batch-{n_files:04d}.parquet"
            pq.write_table(table, table_file)
            print(f"Wrote {len(entries)} entries to {table_file}")
            n_files += 1

    print(f"{time.ctime()} - Finished batch optimization")
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time / 60:.2f} min")
    print("Done!")


if __name__ == "__main__":
    main()
