"""Resume an interrupted B3 benchmark run from its existing JSON output."""

import argparse
import json
from pathlib import Path

from run import generate_circuits_from_data, run_analysis


def load_resume_data(output_path: Path) -> tuple[dict, list[dict]]:
    """Load metadata and completed results from a B3 output file."""
    with output_path.open(encoding="utf-8") as output_file:
        output = json.load(output_file)

    metadata = output.get("metadata")
    results = output.get("results")
    if not isinstance(metadata, dict) or not isinstance(results, list):
        raise ValueError("Output must contain object metadata and list results fields")

    required_fields = ("benchmarks_path", "model", "attempts", "timeout", "prompt_path")
    missing_fields = [field for field in required_fields if field not in metadata]
    if missing_fields:
        raise ValueError(f"Output metadata is missing: {', '.join(missing_fields)}")

    return metadata, results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resume a B3 output file, processing only dataset codes without results."
    )
    parser.add_argument("output", type=Path, help="Existing B3 output JSON file to resume in place")
    parser.add_argument("--analyze", action="store_true", help="Run B3 post-run analysis after resuming")
    args = parser.parse_args()

    output_path = args.output.resolve()
    metadata, results = load_resume_data(output_path)
    completed_names = {result.get("code_name") for result in results if result.get("code_name")}
    print(f"Resuming {output_path}: {len(completed_names)} codes complete.")

    generate_circuits_from_data(
        benchmarks_path=metadata["benchmarks_path"],
        output_path=str(output_path),
        model=metadata["model"],
        harness=metadata.get("harness", "openai"),
        attempts=metadata["attempts"],
        timeout=metadata["timeout"],
        prompt_file=metadata["prompt_path"],
        initial_results=results,
    )
    if args.analyze:
        run_analysis(str(output_path))


if __name__ == "__main__":
    main()