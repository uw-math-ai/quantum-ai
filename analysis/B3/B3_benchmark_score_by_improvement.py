from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "B3"
BENCHMARKS_PATH = ROOT.parent / "data" / "benchmarks.json"
SCORES_DIR = Path(__file__).resolve().parent / "scores"
SCORES_DIR.mkdir(exist_ok=True)
OUTPUT_PATH = SCORES_DIR / "B3_capability_scores_cleaned2.json"

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


def load_stabilizer_counts() -> tuple[dict[str, int], int]:
    with BENCHMARKS_PATH.open() as f:
        benchmarks = json.load(f)
    counts = {entry["name"]: len(entry.get("generators", [])) for entry in benchmarks}
    return counts, sum(counts.values())


def iter_cleaned2_entries(cleaned2_path: Path) -> list[dict]:
    with cleaned2_path.open() as f:
        payload = json.load(f)

    entries: list[dict] = []
    for item in payload.get("cleaned_results", []):
        if isinstance(item, list):
            for entry in item:
                if isinstance(entry, dict):
                    entries.append(entry)
    return entries


def compute_capability_score(cleaned2_path: Path, stabilizer_counts: dict[str, int]) -> dict:
    score = 0
    counted_codes: list[str] = []
    missing_benchmark_entries: list[str] = []

    for entry in iter_cleaned2_entries(cleaned2_path):
        code_name = entry.get("code_name")
        ft_score = entry.get("new_best_output", {}).get("ft_score")
        if not code_name or not ft_score or ft_score == 0:
            continue

        stabilizer_count = stabilizer_counts.get(code_name)
        if stabilizer_count is None:
            missing_benchmark_entries.append(code_name)
            continue

        score += stabilizer_count
        counted_codes.append(code_name)

    return {
        "capability_score": score,
        "num_counted_codes": len(counted_codes),
        "counted_codes": counted_codes,
        "missing_benchmark_entries": sorted(set(missing_benchmark_entries)),
    }


def main() -> None:
    stabilizer_counts, total_stabilizers = load_stabilizer_counts()
    output: dict[str, dict] = {
        "total_benchmark_stabilizers": total_stabilizers,
        "scores": {},
    }

    for date_code, model_paths in RUNS.items():
        output["scores"][date_code] = {}
        for model_name, cleaned2_path in model_paths.items():
            score_data = compute_capability_score(cleaned2_path, stabilizer_counts)
            output["scores"][date_code][model_name] = {
                "cleaned2_file": str(cleaned2_path),
                "capability_score_fraction": f"{score_data['capability_score']} out of {total_stabilizers}",
                **score_data,
            }
            print(
                f"{date_code} | {model_name}: "
                f"{score_data['capability_score']} out of {total_stabilizers} "
                f"(n={score_data['num_counted_codes']})"
            )

    with OUTPUT_PATH.open("w") as f:
        json.dump(output, f, indent=2)
        f.write("\n")
    print(f"Saved capability scores to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
