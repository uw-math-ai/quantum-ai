import json
import os
import sys
import argparse
import time
import stim
from pathlib import Path
from datetime import datetime

# Add tools directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))

from agent import generate_optimized_circuit
from circuit_metric import compute_metrics


def iter_jsonl(path: Path):
    """Yield dict per JSONL line, skipping blanks."""
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_num, json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Bad JSON on line {line_num}: {e}") from e


def normalize_stim_text(stim_text: str) -> str:
    """
    Dataset stores circuits with '\\n'. Convert to real newlines.
    If it's already real newlines, this is harmless.
    """
    return stim_text.replace("\\n", "\n").strip() + "\n"


def optimize_circuits_from_dataset(
    dataset_path: str,
    output_path: str | None = None,
    model: str = "claude-opus-4.6",
    attempts: int = 10,
    timeout: int = 6000,
    prompt_path: str = "optimizer_prompt2.txt",
) -> None:
    """
    Optimize all circuits in a JSONL dataset and write results to a JSON file.

    Each input record is processed independently; failures on one record do not
    affect others.  The output file is re-written after every record so partial
    progress survives crashes.

    Args:
        dataset_path: Path to the input circuit_dataset.jsonl file.
        output_path: Path to save the output JSON file.
            If None, auto-generates as data/<model>/<YYMMdd.HHmm>.json
        model: The model to use for optimization.
        attempts: Number of optimization attempts per circuit.
        timeout: Timeout in seconds for each optimization.
        prompt_path: Path to the prompt template file.
    """
    dataset = Path(dataset_path)
    if not dataset.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset.resolve()}")

    prompt_file = Path(prompt_path)
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file.resolve()}")
    prompt_template = prompt_file.read_text(encoding="utf-8")

    if output_path is None:
        timestamp = datetime.now().strftime("%y%m%d.%H%M")
        out_dir = Path("data") / model
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / f"{timestamp}.json")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "dataset_path": dataset_path,
        "prompt_path": prompt_path,
        "model": model,
        "max_attempts": attempts,
        "timeout": timeout,
        "started_at": datetime.now().isoformat(),
    }
    results: list[dict] = []

    def _save(finished: bool = False) -> None:
        """Re-write the full JSON output (metadata + results so far)."""
        output = {"metadata": {**metadata}, "results": results}
        if finished:
            output["metadata"]["finished_at"] = datetime.now().isoformat()
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

    try:
        for line_num, rec in iter_jsonl(dataset):
            started_at = datetime.now().isoformat()

            # --- extract fields safely ---
            code_name = rec.get("source_code", f"line_{line_num}")
            stabilizers = rec.get("input_stabilizers")
            raw_circuit = rec.get("output_circuit")

            if not stabilizers or not raw_circuit:
                results.append({
                    "code_name": code_name,
                    "status": "missing_fields",
                    "error": "Record is missing 'input_stabilizers' or 'output_circuit'.",
                    "started_at": started_at,
                    "finished_at": datetime.now().isoformat(),
                })
                _save()
                print(f"\n[{len(results)}] {code_name} | SKIP – missing fields")
                continue

            baseline_text = normalize_stim_text(raw_circuit)

            # --- verify baseline parses ---
            try:
                _ = stim.Circuit(baseline_text)
            except Exception as e:
                results.append({
                    "code_name": code_name,
                    "status": "baseline_parse_error",
                    "error": str(e),
                    "started_at": started_at,
                    "finished_at": datetime.now().isoformat(),
                })
                _save()
                print(f"\n[{len(results)}] {code_name} | SKIP – baseline parse error")
                continue

            base_metrics = compute_metrics(baseline_text).as_dict()
            print(f"\n[{len(results) + 1}] {code_name} | base: {base_metrics}")

            # --- run optimizer ---
            try:
                start_time = time.time()
                opt_result = generate_optimized_circuit(
                    stabilizers=stabilizers,
                    initial_circuit=baseline_text,
                    prompt_template=prompt_template,
                    model=model,
                    attempts=attempts,
                    timeout=timeout,
                )
                elapsed_seconds = round(time.time() - start_time, 2)
            except Exception as e:
                results.append({
                    "code_name": code_name,
                    "baseline_circuit": baseline_text,
                    "baseline_metrics": base_metrics,
                    "status": "optimizer_exception",
                    "error": str(e),
                    "started_at": started_at,
                    "finished_at": datetime.now().isoformat(),
                })
                _save()
                print(f"    ✗ optimizer exception: {e}")
                continue

            opt_circ = opt_result.get("circuit")
            evaluations = opt_result.get("evaluations", [])

            if opt_circ is None:
                results.append({
                    "code_name": code_name,
                    "baseline_circuit": baseline_text,
                    "baseline_metrics": base_metrics,
                    "optimized_circuit": None,
                    "valid": False,
                    "better": False,
                    "status": "no_result",
                    "evaluations": evaluations,
                    "elapsed_seconds": elapsed_seconds,
                    "started_at": started_at,
                    "finished_at": datetime.now().isoformat(),
                })
                _save()
                print(f"    ✗ no valid circuit returned  ({elapsed_seconds}s)")
                continue

            opt_text = str(opt_circ)
            opt_metrics = compute_metrics(opt_text).as_dict()

            is_better = (
                (opt_metrics["cx_count"], opt_metrics["volume"], opt_metrics["depth"])
                < (base_metrics["cx_count"], base_metrics["volume"], base_metrics["depth"])
            )

            print(f"    -> opt:  {opt_metrics}  [{'improved' if is_better else 'not_strictly_better'}]  ({elapsed_seconds}s)")

            results.append({
                "code_name": code_name,
                "baseline_circuit": baseline_text,
                "baseline_metrics": base_metrics,
                "optimized_circuit": opt_text,
                "optimized_metrics": opt_metrics,
                "valid": True,
                "better": is_better,
                "evaluations": evaluations,
                "elapsed_seconds": elapsed_seconds,
                "started_at": started_at,
                "finished_at": datetime.now().isoformat(),
            })
            _save()

    finally:
        _save(finished=True)

    total = len(results)
    improved = sum(1 for r in results if r.get("better"))
    print(f"\nDONE. total={total} improved={improved} results={out_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Optimize circuits from a JSONL dataset using an LLM agent"
    )
    parser.add_argument(
        "--dataset",
        default="../data/circuit_dataset.jsonl",
        help="Path to the input circuit_dataset.jsonl file (default: ../data/circuit_dataset.jsonl)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to the output JSON file (default: ./data/<model>/<YYMMdd.HHmm>.json)",
    )
    parser.add_argument(
        "--model",
        default="claude-opus-4.6",
        help="Model to use for optimization (default: claude-opus-4.6)",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=10,
        help="Number of optimization attempts per circuit (default: 10)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=6000,
        help="Timeout in seconds for each optimization (default: 6000)",
    )
    parser.add_argument(
        "--prompt",
        default="optimizer_prompt2.txt",
        help="Path to the prompt template file (default: optimizer_prompt2.txt)",
    )

    args = parser.parse_args()

    optimize_circuits_from_dataset(
        dataset_path=args.dataset,
        output_path=args.output,
        model=args.model,
        attempts=args.attempts,
        timeout=args.timeout,
        prompt_path=args.prompt,
    )


if __name__ == "__main__":
    main()
