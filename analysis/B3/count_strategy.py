from __future__ import annotations

import json
import os
import re
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2] / "B3"
BENCHMARKS_PATH = ROOT.parent / "data" / "benchmarks.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "diagrams"

RUNS = [
    {
        "date_code": "260314",
        "model_files": {
            "claude": {
                "raw": ROOT / "data" / "claude-opus-4.6" / "claude_260314.2351.json",
                "cleaned": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned_260314.2351.json",
            },
            "gemini": {
                "raw": ROOT / "data" / "gemini-3-pro-preview" / "gemini_260314.2353.json",
                "cleaned": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned_260314.2353.json",
            },
            "gpt": {
                "raw": ROOT / "data" / "gpt5.2" / "gpt_260314.2352.json",
                "cleaned": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned_260314.2352.json",
            },
        },
    },
    {
        "date_code": "260319",
        "model_files": {
            "claude": {
                "raw": ROOT / "data" / "claude-opus-4.6" / "claude_260319.0920.json",
                "cleaned": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned_260319.0920.json",
            },
            "gemini": {
                "raw": ROOT / "data" / "gemini-3-pro-preview" / "gemini_260319.1021.json",
                "cleaned": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned_260319.1021.json",
            },
            "gpt": {
                "raw": ROOT / "data" / "gpt5.2" / "gpt_260319.1021.json",
                "cleaned": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned_260319.1021.json",
            },
        },
    },
    {
        "date_code": "260320",
        "model_files": {
            "claude": {
                "raw": ROOT / "data" / "claude-opus-4.6" / "claude_260320.0954.json",
                "cleaned": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned_260320.0954.json",
            },
            "gemini": {
                "raw": ROOT / "data" / "gemini-3-pro-preview" / "gemini_260320.0954.json",
                "cleaned": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned_260320.0954.json",
            },
            "gpt": {
                "raw": ROOT / "data" / "gpt5.2" / "gpt_260320.0954.json",
                "cleaned": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned_260320.0954.json",
            },
        },
    },
    {
        "date_code": "260321",
        "model_files": {
            "claude": {
                "raw": ROOT / "data" / "claude-opus-4.6" / "260321.1013.json",
                "cleaned": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned_260321.1013.json",
            },
            "gemini": {
                "raw": ROOT / "data" / "gemini-3-pro-preview" / "gemini_260321.1013.json",
                "cleaned": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned_260321.1013.json",
            },
            "gpt": {
                "raw": ROOT / "data" / "gpt5.2" / "gpt_260321.1013.json",
                "cleaned": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned_260321.1013.json",
            },
        },
    },
]


def load_benchmark_qubits() -> dict[str, int]:
    with BENCHMARKS_PATH.open() as f:
        benchmarks = json.load(f)
    return {entry["name"]: entry["physical_qubits"] for entry in benchmarks}


def count_qubits_in_circuit(circuit: str) -> int | None:
    qubit_ids = [int(token) for token in re.findall(r"\b\d+\b", circuit)]
    if not qubit_ids:
        return None
    return max(qubit_ids) + 1


def load_raw_circuit_lookup(raw_path: Path) -> dict[str, str]:
    with raw_path.open() as f:
        payload = json.load(f)

    lookup: dict[str, str] = {}
    for result in payload.get("results", []):
        if not isinstance(result, dict):
            continue
        code_name = result.get("code_name")
        circuit = result.get("best_output", {}).get("circuit")
        if code_name and circuit:
            lookup[code_name] = circuit
    return lookup


def iter_cleaned_entries(cleaned_path: Path) -> list[dict]:
    with cleaned_path.open() as f:
        payload = json.load(f)

    entries: list[dict] = []
    for item in payload.get("cleaned_results", []):
        if isinstance(item, list):
            for result in item:
                if isinstance(result, dict):
                    entries.append(result)
    return entries


def classify_strategy_counts(raw_path: Path, cleaned_path: Path, benchmark_qubits: dict[str, int]) -> tuple[int, int, int]:
    same_count = 0
    plus_five_or_less_count = 0
    plus_many_count = 0

    raw_circuits = load_raw_circuit_lookup(raw_path)
    for result in iter_cleaned_entries(cleaned_path):
        code_name = result.get("code_name")
        if result.get("correct") is True:
            circuit = raw_circuits.get(code_name, "")
        else:
            circuit = result.get("new_best_output", {}).get("circuit", "")

        if not code_name or not circuit:
            continue

        before_qubits = benchmark_qubits.get(code_name)
        after_qubits = count_qubits_in_circuit(circuit)
        if before_qubits is None or after_qubits is None:
            continue

        delta = after_qubits - before_qubits
        if delta == 0:
            same_count += 1
        elif 0 < delta <= 5:
            plus_five_or_less_count += 1
        elif delta > 5:
            plus_many_count += 1

    return same_count, plus_five_or_less_count, plus_many_count


def render_histogram(
    title: str,
    model_names: list[str],
    same_counts: list[int],
    plus_five_or_less_counts: list[int],
    plus_many_counts: list[int],
    output_path: Path,
) -> None:
    x_positions = list(range(len(model_names)))
    bar_width = 0.24
    ymax = max(same_counts + plus_five_or_less_counts + plus_many_counts) if any(same_counts + plus_five_or_less_counts + plus_many_counts) else 1

    plt.figure(figsize=(9, 5))
    same_bars = plt.bar(
        [x - bar_width for x in x_positions],
        same_counts,
        width=bar_width,
        color="#2563eb",
        label="No change",
    )
    plus_five_or_less_bars = plt.bar(
        x_positions,
        plus_five_or_less_counts,
        width=bar_width,
        color="#d97706",
        label="<=5 qubits added",
    )
    plus_many_bars = plt.bar(
        [x + bar_width for x in x_positions],
        plus_many_counts,
        width=bar_width,
        color="#059669",
        label=">5 qubits added",
    )

    plt.xlabel("Model")
    plt.ylabel("Count")
    plt.title(title)
    plt.xticks(x_positions, model_names)
    plt.ylim(0, ymax * 1.15)
    plt.legend()

    for bars in [same_bars, plus_five_or_less_bars, plus_many_bars]:
        for bar in bars:
            value = int(bar.get_height())
            y = value + ymax * 0.02 if value else ymax * 0.02
            plt.text(bar.get_x() + bar.get_width() / 2, y, str(value), ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main() -> None:
    benchmark_qubits = load_benchmark_qubits()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for run in RUNS:
        model_names: list[str] = []
        same_counts: list[int] = []
        plus_five_or_less_counts: list[int] = []
        plus_many_counts: list[int] = []

        for model_name, paths in run["model_files"].items():
            same_count, plus_five_or_less_count, plus_many_count = classify_strategy_counts(
                paths["raw"], paths["cleaned"], benchmark_qubits
            )
            model_names.append(model_name)
            same_counts.append(same_count)
            plus_five_or_less_counts.append(plus_five_or_less_count)
            plus_many_counts.append(plus_many_count)
            print(
                f'{run["date_code"]} | {model_name}: '
                f'no_change={same_count}, plus_le_5={plus_five_or_less_count}, plus_gt_5={plus_many_count}'
            )

        output_path = OUTPUT_DIR / f'strategy_count_{run["date_code"]}.png'
        render_histogram(
            title=f'strategy_count_{run["date_code"]}',
            model_names=model_names,
            same_counts=same_counts,
            plus_five_or_less_counts=plus_five_or_less_counts,
            plus_many_counts=plus_many_counts,
            output_path=output_path,
        )
        print(f"Saved histogram to {output_path}")


if __name__ == "__main__":
    main()
