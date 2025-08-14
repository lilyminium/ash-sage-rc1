#!/usr/bin/env bash
#SBATCH -J benchmark
#SBATCH -p standard
#SBATCH -t 16:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16gb
#SBATCH --account dmobley_lab
#SBATCH --output slurm-%x.%A.out

# ===================== conda environment =====================
. ~/.bashrc
conda activate nagl-valence

FORCEFIELD="../forcefields/fb-fit-v2-single-mean_unconstrained.offxml"

python benchmark-mm.py                                          \
        --n-workers                     300                     \
        --worker-type                   "slurm"                 \
        --batch-size                    100                     \
        --memory                        16                      \
        --walltime                      480                     \
        --queue                         "free"                  \
        --conda-environment             "nagl-valence"          \
    -d       "data/optimization"                                \
    -ff      $FORCEFIELD

python benchmark-mm-torsion.py                                  \
        --n-workers                     300                     \
        --worker-type                   "slurm"                 \
        --batch-size                    20                      \
        --memory                        16                      \
        --walltime                      480                     \
        --queue                         "free"                  \
        --conda-environment             "nagl-valence"          \
    -d       "data/torsiondrive"                                \
    -ff      $FORCEFIELD

python get-rmsds-and-tfds.py                                          \
        --n-workers                     300                     \
        --worker-type                   "slurm"                 \
        --batch-size                    200                     \
        --memory                        8                       \
        --walltime                      480                     \
        --queue                         "free"                  \
        --conda-environment             "nagl-valence"          \
    -d       "data/optimization"                     \
    -r       "rmsd-tfd"                     \
    -ff      $FORCEFIELD

python get-all-to-all-rmsd.py                                   \
        --n-workers                     300                     \
        --worker-type                   "slurm"                 \
        --batch-size                    100                     \
        --memory                        16                      \
        --walltime                      480                     \
        --queue                         "free"                  \
        --conda-environment             "nagl-valence"          \
    -ff $FORCEFIELD                                             \
    -d  data/optimization \
    -r  all-to-all-rmsd



# run once
python get-all-to-all-dde.py                                    \
    -i  all-to-all-rmsd \
    -t  0.3 \
    -o  ddes \
    -ff 'Sage 2.0.0' "openff_unconstrained-2.0.0" \
    -ff 'Sage 2.1.0' "openff_unconstrained-2.1.0" \
    -ff 'Sage 2.2.1' "openff_unconstrained-2.2.1" \
    -ff 'Sage 2.3.0rc1' "fb-fit-v2-single-mean_unconstrained"


# python plot-ddes.py \
#     -ff 'Sage 2.0.0' "openff_unconstrained-2.0.0" \
#     -ff 'Sage 2.1.0' "openff_unconstrained-2.1.0" \
#     -ff 'Sage 2.2.1' "openff_unconstrained-2.2.1" \
#     -ff 'Sage 2.3.0rc1' "fb-fit-v2-single-mean_unconstrained" \
#     -i  ddes  -o  images


# python plot-rmsd-tfd.py \
#     -ff 'Sage 2.0.0' "openff_unconstrained-2.0.0" \
#     -ff 'Sage 2.1.0' "openff_unconstrained-2.1.0" \
#     -ff 'Sage 2.2.1' "openff_unconstrained-2.2.1" \
#     -ff 'Sage 2.3.0rc1' "fb-fit-v2-single-mean_unconstrained" \
#     -i rmsd-tfd -o images