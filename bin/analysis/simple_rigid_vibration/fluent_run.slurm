#!/bin/bash -eu
#SBATCH --job-name=HazelFluentRun
#SBATCH --ntasks-per-node=64
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=250G
#SBATCH --time=5-00:00:00
#SBATCH --mail-user=hazel.full@monash.edu
#SBATCH --mail-type=FAIL,END
#SBATCH --output=outFluent.out
#SBATCH --error=errFluent.err
#SBATCH --partition=peach
#SBATCH --qos=peachq

module load ansys/25r1

echo Starting fluent job
fluent 3ddp -i journal.jou -gu -t$SLURM_NTASKS -driver null -scheduler_tight_coupling -pethernet -mpi=openmpi
echo fluent job completed successfully
