from __future__ import annotations

import json
from pathlib import Path


# We calculate the benchmark score here for each LLM.
# Total score = a normalized weighted avgerage
# = sum_{codes} (weight for this code) * (score for codes)

# Score for each codes: we assign score 0 if the edited circuit is invalid, fails verification, or does not preserve all stabilizers. Otherwise, we assign it the FT score of the edited circuit.
# Weight for codes: adjustable. Currently, let the weight be the number of stabilizers of that code.
# We then normalize the total score across all codes (so it'll be a sum of the number of all stabilizers in benchmark file) to get the final benchmark score for each LLM.

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_PATH = ROOT.parent / "data" / "benchmarks.json"
OUTPUT_PATH = Path(__file__).resolve().with_name("rq2_benchmark_scores_cleaned2.json")

RUNS = {
    "260314": {
        "claude": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned2_260314.2351.json",
        "gemini": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned2_260314.2353.json",
        "gpt": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned2_260314.2352.json",
    },
    "260319": {
        "claude": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned2_260319.0920.json",
        "gemini": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned2_260319.1021.json",
        "gpt": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned2_260319.1021.json",
    },
    "260320": {
        "claude": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned2_260320.0954.json",
        "gemini": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned2_260320.0954.json",
        "gpt": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned2_260320.0954.json",
    },
    "260321": {
        "claude": ROOT / "data" / "claude-opus-4.6" / "cleaned" / "cleaned2_260321.1013.json",
        "gemini": ROOT / "data" / "gemini-3-pro-preview" / "cleaned" / "cleaned2_260321.1013.json",
        "gpt": ROOT / "data" / "gpt5.2" / "cleaned" / "cleaned2_260321.1013.json",
    },
}


def load_benchmark_weights() -> tuple[dict[str, int], int]:
    with BENCHMARKS_PATH.open() as f:
        benchmarks = json.load(f)
    weights = {
        entry["name"]: len(entry.get("generators", []))
        for entry in benchmarks
    }
    total_weight = sum(weights.values())
    return weights, total_weight


def iter_entries(cleaned2_path: Path) -> list[dict]:
    with cleaned2_path.open() as f:
        payload = json.load(f)

    entries: list[dict] = []
    for item in payload.get("cleaned_results", []):
        if isinstance(item, list):
            for entry in item:
                if isinstance(entry, dict):
                    entries.append(entry)
    return entries


def is_valid_scored_output(entry: dict, new_best_output: dict) -> bool:
    if not isinstance(new_best_output, dict):
        return False
    if entry.get("correct") is not True:
        return False
    if new_best_output.get("circuit") in (None, ""):
        return False
    if new_best_output.get("ft_score") is None:
        return False
    if new_best_output.get("all_stabilized") is not True:
        return False
    return True


def compute_benchmark_score(cleaned2_path: Path, benchmark_weights: dict[str, int], total_benchmark_weight: int) -> dict:
    weighted_score_sum = 0.0
    num_codes = 0
    num_scored_positive = 0
    missing_weights: list[str] = []

    for entry in iter_entries(cleaned2_path):
        code_name = entry.get("code_name")
        if not code_name:
            continue

        weight = benchmark_weights.get(code_name)
        if weight is None:
            missing_weights.append(code_name)
            continue

        num_codes += 1

        new_best_output = entry.get("new_best_output", {})
        score = float(new_best_output["ft_score"]) if is_valid_scored_output(entry, new_best_output) else 0.0
        if score > 0:
            num_scored_positive += 1
        weighted_score_sum += weight * score

    benchmark_score = (weighted_score_sum / total_benchmark_weight) if total_benchmark_weight else 0.0
    return {
        "benchmark_score": benchmark_score,
        "benchmark_score_fraction": f"{weighted_score_sum:.6f} out of {total_benchmark_weight}",
        "weighted_score_sum": weighted_score_sum,
        "total_weight": total_benchmark_weight,
        "num_codes": num_codes,
        "num_positive_scores": num_scored_positive,
        "missing_benchmark_entries": sorted(set(missing_weights)),
    }


def main() -> None:
    benchmark_weights, total_benchmark_weight = load_benchmark_weights()
    output: dict[str, dict] = {}

    for date_code, model_paths in RUNS.items():
        output[date_code] = {}
        for model_name, cleaned2_path in model_paths.items():
            score_data = compute_benchmark_score(cleaned2_path, benchmark_weights, total_benchmark_weight)
            output[date_code][model_name] = {
                "cleaned2_file": str(cleaned2_path),
                **score_data,
            }
            print(
                f"{date_code} | {model_name}: "
                f"benchmark_score={score_data['benchmark_score_fraction']}, "
                f"num_codes={score_data['num_codes']}, "
                f"num_positive_scores={score_data['num_positive_scores']}"
            )

    with OUTPUT_PATH.open("w") as f:
        json.dump(output, f, indent=2)
        f.write("\n")
    print(f"Saved benchmark scores to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
