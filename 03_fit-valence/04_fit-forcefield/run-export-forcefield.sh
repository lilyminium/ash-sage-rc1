#!/bin/bash
#SBATCH -J export
#SBATCH -p standard
#SBATCH -t 08:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mem=16gb
#SBATCH --constraint=fastscratch
#SBATCH --output slurm-%x.%A.out

date
hostname

source ~/.bashrc
conda activate nagl-valence    

FFNAME=fb-fit-v0-multi-mean
FFNAME=fb-fit-v3-single-mean-k100
FFNAME=fb-fit-v3-single-mean
FFNAME=fb-fit-v3-multi-mean-k100
FFNAME=fb-fit-v2-single-mean
FFNAME=fb-fit-v3-multi-mean
FFNAME=fb-fit-v0-single-mean-k100
FFNAME=fb-fit-sage
FFNAME=fb-fit-v0-single-mean
FFNAME=fb-fit-v2-multi-mean
FFNAME=fb-fit-v4-single-mean-k100
FFNAME=fb-fit-v4-multi-mean-k100
FFNAME=fb-fit-v5-single-mean-k100
FFNAME=fb-fit-v4-multi-mean
FFNAME=fb-fit-v4-single-mean
FFNAME=fb-fit-v5-multi-mean-k100
FFNAME=fb-fit-v5-single-mean-k200
FFNAME=fb-fit-v6-single-mean-k100
FFNAME=fb-fit-v6-multi-mean-k100
FFNAME=fb-fit-v7-single-mean-k100
FFNAME=fb-fit-v8-single-mean-k100
FFNAME=fb-fit-v7-multi-mean-k100
FFNAME=fb-fit-v8-multi-mean-k100
OUTDIR="../../04_benchmark/forcefields"

mkdir -p ${OUTDIR}


INPUTFILE="${FFNAME}/result/optimize/force-field.offxml"
OUTPUTFILE="${OUTDIR}/${FFNAME}.offxml"

python remove_cosmetic_attributes.py -i ${INPUTFILE} -o ${OUTPUTFILE}

