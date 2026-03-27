from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_PATH = ROOT.parent.parent / "data" / "benchmarks.json"

RUNS = [
    {
        "date_code": "260314",
        "display_date": "0314",
        "model_files": {
            "claude": {
                "cleaned": ROOT / "claude-opus-4.6" / "cleaned" / "cleaned_260314.2351.json",
                "raw": ROOT / "claude-opus-4.6" / "claude_260314.2351.json",
            },
            "gemini": {
                "cleaned": ROOT / "gemini-3-pro-preview" / "cleaned" / "cleaned_260314.2353.json",
                "raw": ROOT / "gemini-3-pro-preview" / "gemini_260314.2353.json",
            },
            "gpt": {
                "cleaned": ROOT / "gpt5.2" / "cleaned" / "cleaned_260314.2352.json",
                "raw": ROOT / "gpt5.2" / "gpt_260314.2352.json",
            },
        },
    },
    {
        "date_code": "260319",
        "display_date": "0319",
        "model_files": {
            "claude": {
                "cleaned": ROOT / "claude-opus-4.6" / "cleaned" / "cleaned_260319.0920.json",
                "raw": ROOT / "claude-opus-4.6" / "claude_260319.0920.json",
            },
            "gemini": {
                "cleaned": ROOT / "gemini-3-pro-preview" / "cleaned" / "cleaned_260319.1021.json",
                "raw": ROOT / "gemini-3-pro-preview" / "gemini_260319.1021.json",
            },
            "gpt": {
                "cleaned": ROOT / "gpt5.2" / "cleaned" / "cleaned_260319.1021.json",
                "raw": ROOT / "gpt5.2" / "gpt_260319.1021.json",
            },
        },
    },
    {
        "date_code": "260320",
        "display_date": "0320",
        "model_files": {
            "claude": {
                "cleaned": ROOT / "claude-opus-4.6" / "cleaned" / "cleaned_260320.0954.json",
                "raw": ROOT / "claude-opus-4.6" / "claude_260320.0954.json",
            },
            "gemini": {
                "cleaned": ROOT / "gemini-3-pro-preview" / "cleaned" / "cleaned_260320.0954.json",
                "raw": ROOT / "gemini-3-pro-preview" / "gemini_260320.0954.json",
            },
            "gpt": {
                "cleaned": ROOT / "gpt5.2" / "cleaned" / "cleaned_260320.0954.json",
                "raw": ROOT / "gpt5.2" / "gpt_260320.0954.json",
            },
        },
    },
    {
        "date_code": "260321",
        "display_date": "0321",
        "model_files": {
            "claude": {
                "cleaned": ROOT / "claude-opus-4.6" / "cleaned" / "cleaned_260321.1013.json",
                "raw": ROOT / "claude-opus-4.6" / "260321.1013.json",
            },
            "gemini": {
                "cleaned": ROOT / "gemini-3-pro-preview" / "cleaned" / "cleaned_260321.1013.json",
                "raw": ROOT / "gemini-3-pro-preview" / "gemini_260321.1013.json",
            },
            "gpt": {
                "cleaned": ROOT / "gpt5.2" / "cleaned" / "cleaned_260321.1013.json",
                "raw": ROOT / "gpt5.2" / "260321.1013.json",
            },
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


def _load_cleaned_entries(cleaned_path: Path) -> list[dict]:
    with cleaned_path.open() as f:
        payload = json.load(f)

    entries: list[dict] = []
    for item in payload.get("cleaned_results", []):
        if isinstance(item, list):
            for result in item:
                if isinstance(result, dict):
                    entries.append(result)
    return entries


def _load_raw_lookup(raw_path: Path) -> dict[str, float]:
    with raw_path.open() as f:
        payload = json.load(f)

    lookup: dict[str, float] = {}
    for result in payload.get("results", []):
        if not isinstance(result, dict):
            continue
        code_name = result.get("code_name")
        score = result.get("best_output", {}).get("ft_score")
        if code_name and score is not None:
            lookup[code_name] = score
    return lookup


def collect_effective_ft_scores(cleaned_path: Path, raw_path: Path) -> list[tuple[str, float]]:
    cleaned_entries = _load_cleaned_entries(cleaned_path)
    raw_lookup = _load_raw_lookup(raw_path)
    scores: list[tuple[str, float]] = []

    for result in cleaned_entries:
        code_name = result.get("code_name")
        if not code_name:
            continue

        if result.get("correct") is True:
            score = raw_lookup.get(code_name)
        else:
            score = result.get("new_best_output", {}).get("ft_score")

        if score is not None:
            scores.append((code_name, score))

    return scores


def collect_effective_ft_scores_by_size(
    cleaned_path: Path,
    raw_path: Path,
    benchmark_qubits: dict[str, int],
) -> tuple[list[float], list[float], list[str]]:
    over_80: list[float] = []
    under_or_equal_80: list[float] = []
    missing_names: list[str] = []

    for code_name, score in collect_effective_ft_scores(cleaned_path, raw_path):
        physical_qubits = benchmark_qubits.get(code_name)
        if physical_qubits is None:
            missing_names.append(code_name)
            continue

        if physical_qubits > 80:
            over_80.append(score)
        else:
            under_or_equal_80.append(score)

    return over_80, under_or_equal_80, missing_names
