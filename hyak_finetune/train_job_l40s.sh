#!/bin/bash
#SBATCH --job-name=circuit-llama
#SBATCH --account=cse
#SBATCH --partition=gpu-l40s
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=logs/train_%j.out
#SBATCH --error=logs/train_%j.err

# Same as train_job.sh but targets L40S partition
# L40S has 48GB VRAM - plenty for Llama 8B with 4-bit LoRA

set -e

source "${HOME}/envs/circuit_finetune/bin/activate"

mkdir -p logs

export HF_HOME="/gscratch/cse/${USER}/.cache/huggingface"
export TRANSFORMERS_CACHE="${HF_HOME}/transformers"
mkdir -p "$HF_HOME"

PROJECT_DIR="${HOME}/quantum-ai"
cd "$PROJECT_DIR"

echo "Job started at $(date)"
echo "Node: $(hostname)"
echo "GPUs: $(nvidia-smi -L 2>/dev/null || echo 'none detected')"

python hyak_finetune/train_llama.py \
    --train_data data/finetune_dataset_train.jsonl \
    --val_data data/finetune_dataset_val.jsonl \
    --output_dir models/circuit-llama \
    --model_name meta-llama/Llama-3.1-8B-Instruct \
    --epochs 3 \
    --batch_size 4 \
    --grad_accum 4 \
    --lr 2e-4 \
    --max_seq_length 2048 \
    --lora_r 64 \
    --lora_alpha 16 \
    --logging_steps 10 \
    --save_steps 200

echo "Job finished at $(date)"
