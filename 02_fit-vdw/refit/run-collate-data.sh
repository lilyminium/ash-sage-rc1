#!/usr/bin/env bash
#SBATCH -J collate
#SBATCH -p cpu
#SBATCH -t 1:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --output slurm-%x.%A.out

source ~/.bashrc

conda activate evaluator-050-refit

python collate-data.py
