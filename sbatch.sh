#!/bin/sh
module load intel/2019.1.144
sbatch --nodelist=cu1 --ntasks-per-node=1 run.mineos.drv
