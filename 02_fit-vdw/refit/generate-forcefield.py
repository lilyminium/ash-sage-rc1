import click

from openff.toolkit import ForceField

def main(
    input_forcefield: str = "openff-2.2.1.offxml",
):
    forcefield = ForceField(input_forcefield)