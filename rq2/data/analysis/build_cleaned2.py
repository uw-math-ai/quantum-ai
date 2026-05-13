from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RUNS = [
    {
        "date_code": "260314",
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
        "model_files": {
            "claude": {
                "cleaned": ROOT / "claude-opus-4.6" / "cleaned" / "cleaned_260321.1013.json",
                "raw": ROOT / "claude-opus-4.6" / "claude_260321.1013.json",
            },
            "gemini": {
                "cleaned": ROOT / "gemini-3-pro-preview" / "cleaned" / "cleaned_260321.1013.json",
                "raw": ROOT / "gemini-3-pro-preview" / "gemini_260321.1013.json",
            },
            "gpt": {
                "cleaned": ROOT / "gpt5.2" / "cleaned" / "cleaned_260321.1013.json",
                "raw": ROOT / "gpt5.2" / "gpt_260321.1013.json",
            },
        },
    },
]


def load_cleaned_entries(cleaned_path: Path) -> dict:
    with cleaned_path.open() as f:
        return json.load(f)


def build_raw_best_lookup(raw_path: Path) -> dict[str, dict]:
    with raw_path.open() as f:
        payload = json.load(f)

    best_lookup: dict[str, dict] = {}
    for result in payload.get("results", []):
        if not isinstance(result, dict):
            continue

        code_name = result.get("code_name")
        if not code_name:
            continue

        candidates: list[dict] = []
        best_output = result.get("best_output")
        if isinstance(best_output, dict):
            candidates.append(best_output)

        for candidate in result.get("generated_circuits", []):
            if isinstance(candidate, dict):
                candidates.append(candidate)

        valid_candidates = [
            candidate
            for candidate in candidates
            if candidate.get("all_stabilized") is True and candidate.get("ft_score") is not None
        ]
        if not valid_candidates:
            continue

        best_lookup[code_name] = max(valid_candidates, key=lambda candidate: candidate["ft_score"])

    return best_lookup


def build_cleaned2_payload(cleaned_path: Path, raw_path: Path) -> dict:
    cleaned_payload = load_cleaned_entries(cleaned_path)
    raw_best_lookup = build_raw_best_lookup(raw_path)

    cleaned2_payload = deepcopy(cleaned_payload)
    rebuilt_results: list = []

    for item in cleaned_payload.get("cleaned_results", []):
        if not isinstance(item, list):
            rebuilt_results.append(item)
            continue

        rebuilt_entries: list[dict] = []
        for entry in item:
            if not isinstance(entry, dict):
                rebuilt_entries.append(entry)
                continue

            if entry.get("correct") is False:
                rebuilt_entries.append(entry)
                continue

            code_name = entry.get("code_name")
            best_candidate = raw_best_lookup.get(code_name)
            if best_candidate is None:
                rebuilt_entries.append(entry)
                continue

            rebuilt_entry = deepcopy(entry)
            rebuilt_entry["new_best_output"] = {
                key: value
                for key, value in best_candidate.items()
                if key in {"circuit", "ft_score", "all_stabilized", "preserved_stabilizers", "ft_check", "stabilizer_details", "ALL TRUE"}
            }
            rebuilt_entries.append(rebuilt_entry)

        rebuilt_results.append(rebuilt_entries)

    cleaned2_payload["cleaned_results"] = rebuilt_results
    return cleaned2_payload


def main() -> None:
    for run in RUNS:
        for model_name, paths in run["model_files"].items():
            cleaned_path = paths["cleaned"]
            raw_path = paths["raw"]
            cleaned2_payload = build_cleaned2_payload(cleaned_path, raw_path)
            cleaned2_path = cleaned_path.with_name(cleaned_path.name.replace("cleaned_", "cleaned2_", 1))
            with cleaned2_path.open("w") as f:
                json.dump(cleaned2_payload, f, indent=2)
                f.write("\n")
            print(f"Created {cleaned2_path} from {model_name} {run['date_code']}")


if __name__ == "__main__":
    main()
