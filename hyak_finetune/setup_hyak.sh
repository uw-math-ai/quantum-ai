#!/bin/bash
# Run this ONCE on Hyak to set up the environment
# Usage: bash setup_hyak.sh

set -e

echo "=== Setting up Llama fine-tuning environment ==="

# Create virtual environment
VENV_DIR="${HOME}/envs/circuit_finetune"
if [ -d "$VENV_DIR" ]; then
    echo "Environment already exists at $VENV_DIR"
else
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing packages..."
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install \
    transformers>=4.44.0 \
    datasets \
    accelerate \
    peft>=0.12.0 \
    trl>=0.9.0 \
    bitsandbytes \
    scipy \
    wandb \
    flash-attn --no-build-isolation

echo ""
echo "=== Logging in to Hugging Face ==="
echo "You need a token from https://huggingface.co/settings/tokens"
echo "Make sure you've accepted Meta's Llama license at:"
echo "  https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct"
echo ""
huggingface-cli login

echo ""
echo "=== Setup complete ==="
echo "Environment: $VENV_DIR"
echo "Activate with: source $VENV_DIR/bin/activate"