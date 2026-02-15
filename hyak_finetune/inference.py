"""
Test the fine-tuned Llama model on circuit generation.

Usage:
    python inference.py \
        --model_dir models/circuit-llama/final \
        --stabilizers "XZZXI,IXZZX,XIXZZ,ZXIXZ"

    # Or test on benchmark codes:
    python inference.py \
        --model_dir models/circuit-llama/final \
        --benchmarks data/benchmarks.json \
        --max_qubits 20 \
        --num_trials 5
"""

from __future__ import annotations

import argparse
import json
import sys
import os
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# Add project root to path for check_stabilizers
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.check_stabilizers import check_stabilizers


SYSTEM_PROMPT = (
    "You are an expert quantum circuit designer. Given a set of stabilizer generators, "
    "output a Stim circuit that prepares a quantum state stabilized by all given generators. "
    "Use only these gates: H, S, CX (CNOT), X, Y, Z. "
    "Output ONLY valid Stim circuit instructions, one per line. No explanations."
)


def load_model(model_dir: str, use_4bit: bool = True):
    """Load the fine-tuned model."""
    print(f"Loading model from {model_dir}...")

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs = {
        "torch_dtype": torch.bfloat16,
        "device_map": "auto",
    }

    if use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        model_kwargs["quantization_config"] = bnb_config

    model = AutoModelForCausalLM.from_pretrained(model_dir, **model_kwargs)

    return model, tokenizer


def generate_circuit(
    model,
    tokenizer,
    stabilizers: list[str],
    max_new_tokens: int = 1024,
    temperature: float = 0.1,
) -> str:
    """Generate a circuit for the given stabilizers."""
    num_qubits = len(stabilizers[0])
    stab_str = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(stabilizers))

    user_msg = (
        f"Design a Stim circuit that prepares a state stabilized by "
        f"these {len(stabilizers)} generators on {num_qubits} qubits:\n\n"
        f"{stab_str}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    input_text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode only the new tokens
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True)

    return response.strip()


def evaluate_circuit(circuit_str: str, stabilizers: list[str]) -> dict:
    """Check if a generated circuit satisfies all stabilizers."""
    try:
        results = check_stabilizers(circuit_str, stabilizers)
        satisfied = sum(results.values())
        total = len(stabilizers)
        return {
            "satisfied": satisfied,
            "total": total,
            "all_satisfied": satisfied == total,
            "per_stabilizer": results,
        }
    except Exception as e:
        return {
            "satisfied": 0,
            "total": len(stabilizers),
            "all_satisfied": False,
            "error": str(e),
        }


def test_single(model, tokenizer, stabilizers: list[str], num_trials: int = 1):
    """Test on a single set of stabilizers."""
    num_qubits = len(stabilizers[0])
    print(f"\nStabilizers ({num_qubits} qubits, {len(stabilizers)} generators):")
    for s in stabilizers:
        print(f"  {s}")

    for trial in range(num_trials):
        print(f"\n--- Trial {trial + 1} ---")
        circuit = generate_circuit(model, tokenizer, stabilizers)
        print(f"Circuit:\n{circuit}\n")

        result = evaluate_circuit(circuit, stabilizers)
        if "error" in result:
            print(f"ERROR: {result['error']}")
        else:
            print(f"Result: {result['satisfied']}/{result['total']} satisfied")
            for stab, ok in result["per_stabilizer"].items():
                status = "✓" if ok else "✗"
                print(f"  {status} {stab}")


def test_benchmarks(
    model, tokenizer, benchmarks_path: str,
    max_qubits: int = 50, num_trials: int = 3,
):
    """Test on benchmark codes."""
    with open(benchmarks_path) as f:
        codes = json.load(f)

    codes = [c for c in codes if c["physical_qubits"] <= max_qubits]
    print(f"Testing on {len(codes)} codes with <= {max_qubits} qubits\n")

    results_summary = []

    for code in codes:
        name = code["name"]
        stabilizers = code["generators"]
        nq = code["physical_qubits"]

        print(f"\n{'='*60}")
        print(f" {name} ({nq} qubits, {len(stabilizers)} stabilizers)")
        print(f"{'='*60}")

        trial_results = []
        for trial in range(num_trials):
            circuit = generate_circuit(model, tokenizer, stabilizers)
            result = evaluate_circuit(circuit, stabilizers)
            trial_results.append(result)

            status = "✓" if result["all_satisfied"] else "✗"
            print(f"  Trial {trial+1}: {status} {result['satisfied']}/{result['total']}")

        best = max(trial_results, key=lambda r: r["satisfied"])
        solved = sum(1 for r in trial_results if r["all_satisfied"])

        results_summary.append({
            "name": name,
            "qubits": nq,
            "stabilizers": len(stabilizers),
            "best_satisfied": best["satisfied"],
            "solved_trials": solved,
            "total_trials": num_trials,
        })

    # Print summary
    print(f"\n{'='*70}")
    print(f" SUMMARY")
    print(f"{'='*70}")
    print(f" {'Code':<30} {'Qubits':>6} {'Stabs':>6} {'Best':>8} {'Solved':>8}")
    print(f" {'-'*30} {'-'*6} {'-'*6} {'-'*8} {'-'*8}")

    total_solved = 0
    for s in results_summary:
        solved_str = f"{s['solved_trials']}/{s['total_trials']}"
        print(
            f" {s['name']:<30} {s['qubits']:>6} "
            f"{s['stabilizers']:>6} "
            f"{s['best_satisfied']}/{s['stabilizers']:>5} "
            f"{solved_str:>8}"
        )
        if s["solved_trials"] > 0:
            total_solved += 1

    print(f"\n Codes with at least 1 solve: {total_solved}/{len(results_summary)}")


def main():
    parser = argparse.ArgumentParser(description="Test fine-tuned circuit generator")
    parser.add_argument("--model_dir", type=str, required=True)
    parser.add_argument("--stabilizers", type=str, default=None,
                        help="Comma-separated stabilizer strings")
    parser.add_argument("--benchmarks", type=str, default=None,
                        help="Path to benchmarks JSON")
    parser.add_argument("--max_qubits", type=int, default=50)
    parser.add_argument("--num_trials", type=int, default=3)
    parser.add_argument("--no_4bit", action="store_true")
    args = parser.parse_args()

    model, tokenizer = load_model(args.model_dir, use_4bit=not args.no_4bit)

    if args.stabilizers:
        stabilizers = args.stabilizers.split(",")
        test_single(model, tokenizer, stabilizers, args.num_trials)
    elif args.benchmarks:
        test_benchmarks(model, tokenizer, args.benchmarks, args.max_qubits, args.num_trials)
    else:
        # Default test
        test_single(
            model, tokenizer,
            ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"],
            num_trials=3,
        )


if __name__ == "__main__":
    main()
