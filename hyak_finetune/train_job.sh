#!/bin/bash
#SBATCH --job-name=circuit-llama
#SBATCH --account=cse
#SBATCH --partition=gpu-a100
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=logs/train_%j.out
#SBATCH --error=logs/train_%j.err

# ==============================================================
# Fine-tune Llama 3.1 8B on quantum circuit generation
#
# Before first run:
#   1. bash setup_hyak.sh  (installs env + HF login)
#   2. Generate data:
#      python data/generate_circuit_dataset.py \
#          -b data/benchmarks.json -n 50000 \
#          --max-qubits 50 \
#          -o data/circuit_large.jsonl
#   3. Format for fine-tuning:
#      python format_for_finetuning.py \
#          --input data/circuit_large.jsonl \
#          --output data/finetune_dataset.jsonl \
#          --max_qubits 50
#
# Submit: sbatch train_job.sh
# ==============================================================

set -e

# Activate environment
source "${HOME}/envs/circuit_finetune/bin/activate"

# Create logs directory
mkdir -p logs

# Set cache directories to scratch (avoid filling home quota)
export HF_HOME="/gscratch/cse/${USER}/.cache/huggingface"
export TRANSFORMERS_CACHE="${HF_HOME}/transformers"
mkdir -p "$HF_HOME"

# Project directory - UPDATE THIS to your actual path
PROJECT_DIR="${HOME}/quantum-ai"
cd "$PROJECT_DIR"

echo "Job started at $(date)"
echo "Node: $(hostname)"
echo "GPUs: $(nvidia-smi -L 2>/dev/null || echo 'none detected')"
echo "Project dir: $PROJECT_DIR"

# Run training
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
