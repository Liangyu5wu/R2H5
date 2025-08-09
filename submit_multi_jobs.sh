#!/bin/bash

# Usage: ./submit_multi_jobs.sh

BASE_DIR="/fs/ddn/sdf/group/atlas/d/liangyu/jetML/datasets/h5"

SUBMIT_DIR="job_submissions_$(date +%Y%m%d_%H%M%S)"
mkdir -p $SUBMIT_DIR
echo "Created submission directory: $SUBMIT_DIR"



for i in {0..42}; do
    JOB_NUM=$(printf "%03d" $i)
    JOB_NAME="job_${JOB_NUM}"
    BATCH_SCRIPT="${SUBMIT_DIR}/testbatch_${JOB_NAME}.sh"
    
    cat > $BATCH_SCRIPT << EOF
#!/bin/bash
#
#SBATCH --account=atlas:default
#SBATCH --partition=roma
#SBATCH --job-name=h5_${JOB_NUM}
#SBATCH --output=${SUBMIT_DIR}/output_job${JOB_NUM}-%j.txt
#SBATCH --error=${SUBMIT_DIR}/error_job${JOB_NUM}-%j.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8g
#SBATCH --time=10:00:00

cd ${BASE_DIR}
source setup.sh
echo "Setup!"

python process_h5_old_files.py --input-dir ./Vertex_timing_old_files --output-dir ./selected_h5_old_files --start-idx $i --end-idx $i
EOF
    
    chmod +x $BATCH_SCRIPT
    
    echo "Submitting job for $JOB_NUM"
    sbatch $BATCH_SCRIPT
done

echo "All jobs have been submitted"
echo "All submission files are saved in directory: $SUBMIT_DIR"
