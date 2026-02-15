"""
Format circuit dataset into Llama fine-tuning format.

Takes the existing JSONL with {input_stabilizers, output_circuit} entries
and formats them as instruction/response pairs for LLM fine-tuning.

Usage:
    python format_for_finetuning.py \
        --input data/circuit_large.jsonl \
        --output data/finetune_dataset.jsonl \
        --max_qubits 50
"""

import argparse
import json
import random
from pathlib import Path


SYSTEM_PROMPT = (
    "You are an expert quantum circuit designer. Given a set of stabilizer generators, "
    "output a Stim circuit that prepares a quantum state stabilized by all given generators. "
    "Use only these gates: H, S, CX (CNOT), X, Y, Z. "
    "Output ONLY valid Stim circuit instructions, one per line. No explanations."
)


def format_stabilizers(stabilizers: list[str]) -> str:
    """Format stabilizer list into a readable prompt."""
    return "\n".join(f"  {i+1}. {s}" for i, s in enumerate(stabilizers))


def format_circuit(circuit_str: str) -> str:
    """Clean up circuit string from JSONL format."""
    # Handle escaped newlines
    circuit = circuit_str.replace("\\n", "\n").strip()
    # Remove empty lines
    lines = [l.strip() for l in circuit.split("\n") if l.strip()]
    return "\n".join(lines)


def create_training_example(entry: dict) -> dict | None:
    """Convert a dataset entry to a fine-tuning example."""
    stabilizers = entry.get("input_stabilizers", [])
    circuit_str = entry.get("output_circuit", "")
    source = entry.get("source_code", "unknown")

    if not stabilizers or not circuit_str:
        return None

    num_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)

    user_msg = (
        f"Design a Stim circuit that prepares a state stabilized by "
        f"these {num_stabilizers} generators on {num_qubits} qubits:\n\n"
        f"{format_stabilizers(stabilizers)}"
    )

    circuit = format_circuit(circuit_str)
    if not circuit:
        return None

    # Llama 3.1 chat format
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": circuit},
        ],
        "source_code": source,
        "num_qubits": num_qubits,
    }


def main():
    parser = argparse.ArgumentParser(description="Format dataset for LLM fine-tuning")
    parser.add_argument("--input", "-i", type=str, required=True)
    parser.add_argument("--output", "-o", type=str, required=True)
    parser.add_argument("--max_qubits", type=int, default=50)
    parser.add_argument("--val_split", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    # Load dataset
    with open(args.input) as f:
        entries = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(entries)} entries from {args.input}")

    # Filter by qubit count
    entries = [
        e for e in entries
        if e.get("input_stabilizers") and len(e["input_stabilizers"][0]) <= args.max_qubits
    ]
    print(f"After filtering to <= {args.max_qubits} qubits: {len(entries)}")

    # Format
    examples = []
    skipped = 0
    for entry in entries:
        ex = create_training_example(entry)
        if ex:
            examples.append(ex)
        else:
            skipped += 1

    print(f"Formatted {len(examples)} examples ({skipped} skipped)")

    # Shuffle
    random.shuffle(examples)

    # Split train/val
    val_size = int(len(examples) * args.val_split)
    train_examples = examples[val_size:]
    val_examples = examples[:val_size]

    # Save
    output_path = Path(args.output)
    train_path = output_path.with_stem(output_path.stem + "_train")
    val_path = output_path.with_stem(output_path.stem + "_val")

    for path, data, name in [
        (train_path, train_examples, "train"),
        (val_path, val_examples, "val"),
    ]:
        with open(path, "w") as f:
            for ex in data:
                f.write(json.dumps(ex) + "\n")
        print(f"Saved {len(data)} {name} examples to {path}")

    # Stats
    qubit_counts = {}
    for ex in examples:
        nq = ex["num_qubits"]
        qubit_counts[nq] = qubit_counts.get(nq, 0) + 1

    print(f"\nQubit distribution:")
    for nq in sorted(qubit_counts):
        print(f"  {nq} qubits: {qubit_counts[nq]} examples")

    # Token length estimate
    avg_len = sum(
        len(ex["messages"][1]["content"]) + len(ex["messages"][2]["content"])
        for ex in examples
    ) / len(examples)
    est_tokens = avg_len / 4  # rough char-to-token ratio
    print(f"\nAvg prompt+completion length: {avg_len:.0f} chars (~{est_tokens:.0f} tokens)")


if __name__ == "__main__":
    main()