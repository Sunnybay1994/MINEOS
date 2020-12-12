#!/bin/sh

# Lines begin with "#SBATCH" set slurm parameters.
# Lines begin with "#" except "#!" and "#SBATCH" are comments.
# Slurm parameters must appear before shell command. 

# Useage: sbatch intel.sh
# Output: slurm-<JOB_ID>.out

#SBATCH --get-user-env
#SBATCH --mail-type=end

######### set job's name
#SBATCH -J mineos_mpi
#SBATCH -o slurm-%j.out
#SBATCH -e slurm-%j.err

######### set NODE and TASK values(CORES = nodes * ntasks-per-node)
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=24

######### set Parallel Environment
## load environment before submitting this job
module load intel/2020.4.304
export FI_PROVIDER=sockets
export I_MPI_FABRICS=ofi
export FI_SOCKETS_IFACE=ib0

echo "PATH = $PATH"
echo "LD_LIBRARY_PATH = $LD_LIBRARY_PATH"
WORKPATH=`pwd`
echo "Current Directory = $WORKPATH"

#env|sort|grep "SLURM"

#########  execute PROGRAM_NAME
#
OUTDIR="./tmp"
MODNAM="PREMQL6ic_21808e.card"
MODPAT="."
#
echo Running mineos_drv
#
# Set the running arguments.
GRAV="2000."
LMIN="1"
LMAX="1000"
EPS="1.d-12"
FMIN="-1."
FMAX="50.5"
CHKERR="1.d-2"
#
echo Running mineos_mpi with arguments
echo model file: $MODPAT/$MODNAM
echo grav=$GRAV 
echo lmin=$LMIN 
echo lmax=$LMAX 
echo eps=$EPS
echo fmhzmin=$FMIN 
echo fmhzmax=$FMAX 
echo Output directory: $OUTDIR
#
mkdir -p $OUTDIR

echo  "Computing is started at $(date)."

srun hostname | sort -n > slurm.hosts
#sed -i -e 's|compute|fast|g' -e 's|.local||g' slurm.hosts



# -n CORES
$MPI_HOME/bin/mpiexec -n 96 -iface ib0 -machinefile slurm.hosts -wdir $WORKPATH $WORKPATH/mineos_mpi $MODPAT $MODNAM $OUTDIR $GRAV $LMIN $LMAX $EPS $FMIN $FMAX $CHKERR
exit_code=$?
/bin/rm -f slurm.hosts

echo  "Computing is stopped at $(date)."
exit $exit_code
