"""Resume an interrupted B2 benchmark run from its existing JSON output."""

import argparse
import json
from pathlib import Path

from run import optimize_circuits_from_dataset


def load_resume_data(output_path: Path) -> tuple[dict, list[dict]]:
    """Load metadata and completed results from a B2 output file."""
    with output_path.open(encoding="utf-8") as output_file:
        output = json.load(output_file)

    metadata = output.get("metadata")
    results = output.get("results")
    if not isinstance(metadata, dict) or not isinstance(results, list):
        raise ValueError("Output must contain object metadata and list results fields")

    required_fields = ("dataset_path", "model", "max_attempts", "timeout", "prompt_path")
    missing_fields = [field for field in required_fields if field not in metadata]
    if missing_fields:
        raise ValueError(f"Output metadata is missing: {', '.join(missing_fields)}")

    return metadata, results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resume a B2 output file, processing only dataset codes without results."
    )
    parser.add_argument("output", type=Path, help="Existing B2 output JSON file to resume in place")
    args = parser.parse_args()

    output_path = args.output.resolve()
    metadata, results = load_resume_data(output_path)
    completed_names = {result.get("code_name") for result in results if result.get("code_name")}
    print(f"Resuming {output_path}: {len(completed_names)} codes complete.")

    optimize_circuits_from_dataset(
        dataset_path=metadata["dataset_path"],
        output_path=str(output_path),
        model=metadata["model"],
        harness=metadata.get("harness", "openai"),
        attempts=metadata["max_attempts"],
        timeout=metadata["timeout"],
        prompt_path=metadata["prompt_path"],
        limit=metadata.get("limit"),
        initial_results=results,
    )


if __name__ == "__main__":
    main()