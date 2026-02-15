"""
Fine-tune Llama 3.1 8B Instruct on quantum circuit generation.

Uses LoRA for parameter-efficient training.
Designed for Hyak (SLURM cluster with A100/L40S GPUs).

Usage:
    python train_llama.py \
        --train_data data/finetune_dataset_train.jsonl \
        --val_data data/finetune_dataset_val.jsonl \
        --output_dir models/circuit-llama \
        --epochs 3
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer, SFTConfig


def load_jsonl_dataset(train_path: str, val_path: str | None = None):
    """Load JSONL files as HuggingFace datasets."""
    data_files = {"train": train_path}
    if val_path:
        data_files["validation"] = val_path
    return load_dataset("json", data_files=data_files)


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Llama on circuit generation")
    parser.add_argument("--train_data", type=str, required=True)
    parser.add_argument("--val_data", type=str, default=None)
    parser.add_argument("--output_dir", type=str, default="models/circuit-llama")
    parser.add_argument("--model_name", type=str, default="meta-llama/Llama-3.1-8B-Instruct")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--grad_accum", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max_seq_length", type=int, default=2048)
    parser.add_argument("--lora_r", type=int, default=64)
    parser.add_argument("--lora_alpha", type=int, default=16)
    parser.add_argument("--lora_dropout", type=float, default=0.1)
    parser.add_argument("--use_4bit", action="store_true", default=True)
    parser.add_argument("--no_4bit", action="store_true")
    parser.add_argument("--bf16", action="store_true", default=True)
    parser.add_argument("--logging_steps", type=int, default=10)
    parser.add_argument("--save_steps", type=int, default=200)
    parser.add_argument("--warmup_ratio", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.no_4bit:
        args.use_4bit = False

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'='*60}")
    print(f"Fine-tuning {args.model_name}")
    print(f"Train data: {args.train_data}")
    print(f"Val data: {args.val_data}")
    print(f"Output: {args.output_dir}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch_size} x {args.grad_accum} grad accum")
    print(f"LoRA r={args.lora_r}, alpha={args.lora_alpha}")
    print(f"4-bit quantization: {args.use_4bit}")
    print(f"{'='*60}\n")

    # ---- Load tokenizer ----
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # ---- Load model ----
    print("Loading model...")
    model_kwargs = {
        "torch_dtype": torch.bfloat16 if args.bf16 else torch.float16,
        "device_map": "auto",
        "use_cache": False,  # Required for gradient checkpointing
    }

    if args.use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16 if args.bf16 else torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        model_kwargs["quantization_config"] = bnb_config

    model = AutoModelForCausalLM.from_pretrained(args.model_name, **model_kwargs)

    # ---- LoRA config ----
    print("Applying LoRA...")
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        bias="none",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ---- Load dataset ----
    print("Loading dataset...")
    dataset = load_jsonl_dataset(args.train_data, args.val_data)
    print(f"Train examples: {len(dataset['train'])}")
    if "validation" in dataset:
        print(f"Val examples: {len(dataset['validation'])}")

    # ---- Format messages using chat template ----
    def format_example(example):
        """Apply Llama chat template to messages."""
        messages = example["messages"]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        return {"text": text}

    dataset = dataset.map(format_example, remove_columns=dataset["train"].column_names)

    # ---- Training config ----
    effective_batch = args.batch_size * args.grad_accum
    total_steps = (len(dataset["train"]) // effective_batch) * args.epochs
    print(f"Effective batch size: {effective_batch}")
    print(f"Estimated total steps: {total_steps}")

    training_args = SFTConfig(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=args.warmup_ratio,
        bf16=args.bf16,
        fp16=not args.bf16,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=3,
        eval_strategy="steps" if "validation" in dataset else "no",
        eval_steps=args.save_steps if "validation" in dataset else None,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        max_seq_length=args.max_seq_length,
        dataset_text_field="text",
        seed=args.seed,
        report_to="none",
    )

    # ---- Trainer ----
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset.get("validation"),
        processing_class=tokenizer,
    )

    # ---- Train ----
    print("\nStarting training...")
    trainer.train()

    # ---- Save ----
    print("\nSaving model...")
    trainer.save_model(str(output_dir / "final"))
    tokenizer.save_pretrained(str(output_dir / "final"))

    print(f"\nTraining complete!")
    print(f"Model saved to {output_dir / 'final'}")
    print(f"\nTo merge LoRA weights and export:")
    print(f"  python merge_and_export.py --model_dir {output_dir / 'final'}")


if __name__ == "__main__":
    main()
