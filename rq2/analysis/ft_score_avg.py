from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_PATH = ROOT.parent / "data" / "benchmarks.json"

RUNS = [
    {
        "date_code": "260314",
        "display_date": "0314",
        "model_files": {
            "claude": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned2_260314.2351.json",
            "gemini": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned2_260314.2353.json",
            "gpt": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned2_260314.2352.json",
        },
    },
    {
        "date_code": "260319",
        "display_date": "0319",
        "model_files": {
            "claude": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned2_260319.0920.json",
            "gemini": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned2_260319.1021.json",
            "gpt": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned2_260319.1021.json",
        },
    },
    {
        "date_code": "260320",
        "display_date": "0320",
        "model_files": {
            "claude": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned2_260320.0954.json",
            "gemini": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned2_260320.0954.json",
            "gpt": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned2_260320.0954.json",
        },
    },
    {
        "date_code": "260321",
        "display_date": "0321",
        "model_files": {
            "claude": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned2_260321.1013.json",
            "gemini": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned2_260321.1013.json",
            "gpt": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned2_260321.1013.json",
        },
    },
]


def load_benchmark_qubits() -> dict[str, int]:
    with BENCHMARKS_PATH.open() as f:
        benchmarks = json.load(f)
    return {entry["name"]: entry["physical_qubits"] for entry in benchmarks}


def average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def load_cleaned2_entries(cleaned2_path: Path) -> list[dict]:
    with cleaned2_path.open() as f:
        payload = json.load(f)

    entries: list[dict] = []
    for item in payload.get("cleaned_results", []):
        if isinstance(item, list):
            for result in item:
                if isinstance(result, dict):
                    entries.append(result)
    return entries


def collect_ft_scores(cleaned2_path: Path) -> list[tuple[str, float]]:
    scores: list[tuple[str, float]] = []
    for result in load_cleaned2_entries(cleaned2_path):
        code_name = result.get("code_name")
        score = result.get("new_best_output", {}).get("ft_score")
        if code_name and score is not None:
            scores.append((code_name, score))
    return scores


def collect_ft_scores_by_size(
    cleaned2_path: Path,
    benchmark_qubits: dict[str, int],
) -> tuple[list[float], list[float], list[str]]:
    over_80: list[float] = []
    under_or_equal_80: list[float] = []
    missing_names: list[str] = []

    for code_name, score in collect_ft_scores(cleaned2_path):
        physical_qubits = benchmark_qubits.get(code_name)
        if physical_qubits is None:
            missing_names.append(code_name)
            continue

        if physical_qubits > 80:
            over_80.append(score)
        else:
            under_or_equal_80.append(score)

    return over_80, under_or_equal_80, missing_names
