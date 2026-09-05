"""Resume an interrupted B1 benchmark run from its existing JSON output."""

import argparse
import json
from pathlib import Path

from run import generate_circuits_from_benchmarks


def load_resume_data(output_path: Path) -> tuple[dict, list[dict]]:
    """Load metadata and completed results from a B1 output file."""
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
        description="Resume a B1 output file, processing only benchmark codes without results."
    )
    parser.add_argument("output", type=Path, help="Existing B1 output JSON file to resume in place")
    args = parser.parse_args()

    output_path = args.output.resolve()
    metadata, results = load_resume_data(output_path)
    completed_names = {result.get("code_name") for result in results if result.get("code_name")}

    with open(metadata["benchmarks_path"], encoding="utf-8") as benchmark_file:
        benchmark_count = len(json.load(benchmark_file))

    print(
        f"Resuming {output_path}: {len(completed_names)}/{benchmark_count} codes complete; "
        f"{benchmark_count - len(completed_names)} queued."
    )
    generate_circuits_from_benchmarks(
        benchmarks_path=metadata["benchmarks_path"],
        output_path=str(output_path),
        model=metadata["model"],
        harness=metadata.get("harness", "openai"),
        attempts=metadata["attempts"],
        timeout=metadata["timeout"],
        prompt_file=metadata["prompt_path"],
        initial_results=results,
    )


if __name__ == "__main__":
    main()