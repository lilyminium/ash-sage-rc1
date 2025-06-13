import pathlib
import tqdm

from collections import defaultdict
import pandas as pd

from openff.evaluator.client.client import RequestResult
from openff.evaluator.datasets.datasets import PhysicalPropertyDataSet


def main():
    reference = PhysicalPropertyDataSet.from_json("targets/phys-prop/training-set.json")
    directory = pathlib.Path("optimize.tmp")
    results_files = sorted(directory.glob("phys-prop/iter*/results.json"))

    data_over_iterations = {}
    for prop in reference.properties:
        data_over_iterations[prop.id] = [
            type(prop).__name__, prop.value.m
        ]

    iter_cols = []
    for result_file in tqdm.tqdm(results_files):
        iter_cols.append(result_file.parent.name)
        result = RequestResult.from_json(result_file)
        dataset = result.estimated_properties
        for prop in dataset.properties:
            data_over_iterations[prop.id].append(prop.value.m)

    df = pd.DataFrame.from_dict(
        data_over_iterations,
        orient="index",
        columns=["Property type", "Reference"] + iter_cols
    )
    output_file = "training_per_iteration.csv"
    df.to_csv(output_file)
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()
