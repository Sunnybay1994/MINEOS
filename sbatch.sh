#!/bin/sh
module load intel/2020.4.304
sbatch --nodelist=cu2 --ntasks-per-node=1 run.mineos.drv
# sbatch --nodelist=cu7 --ntasks-per-node=24 recal_missing_modes.py 