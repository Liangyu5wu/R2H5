import r2h5

def get_slurm_script(
        job_name, 
        config_path,
        debug,
        file_name, 
        file_index_offset,
        job_path, 
        time="00:30:00", 
        memory=4,
        partition="roma",
        account="atlas:usatlas",
        cpu_count=1,
    ):
    """Return a Slurm script for batch processing."""
    slurm_script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --account={account}
#SBATCH --output={job_path}/logs/{job_name}-%j.%x.%A_%a.out
#SBATCH --error={job_path}/logs/{job_name}-%j.%x.%A_%a.err
#SBATCH --ntasks=1
#SBATCH --time={time}
#SBATCH --cpus-per-task={cpu_count}
#SBATCH --mem={memory}G

cd {r2h5.__package_path__}/R2H5
if type setup_conda &>/dev/null; then
    echo "The function 'setup_conda' exists - running it."
    setup_conda
else
    echo "The function 'setup_conda' does not exist."
fi
source /sdf/group/fermi/sw/conda/bin/activate fermitools-2.4.0
conda activate r2h5
echo "r2h5 got activated!"
pwd
r2h5 -c {config_path} -i {file_name} --file-index-offset {file_index_offset} {"--debug" if debug else ""}
"""
    return slurm_script