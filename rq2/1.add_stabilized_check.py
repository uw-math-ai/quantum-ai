#%%
import json
import os
import sys
import glob
import argparse

# Add tools directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))

from check_stabilizers import check_stabilizers


def load_benchmarks(benchmarks_path: str) -> dict[str, list[str]]:
    """Load benchmarks and return a mapping from source_code (code_name) to input_stabilizers."""
    mapping = {}
    with open(benchmarks_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            mapping[entry["source_code"]] = entry["input_stabilizers"]
    return mapping


def process_outcome_file(filepath: str, stabilizers_map: dict[str, list[str]]) -> int:
    """Add all_stabilized field to each generated_circuit entry in an outcome file.
    
    Returns the number of circuits updated.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for result in data.get("results", []):
        code_name = result.get("code_name")
        if code_name not in stabilizers_map:
            print(f"  ⚠ Unknown code_name '{code_name}' in {filepath}, skipping")
            continue

        input_stabilizers = stabilizers_map[code_name]

        for circuit_entry in result.get("generated_circuits", []):
            circuit_str = circuit_entry.get("circuit")
            if circuit_str is None:
                continue

            try:
                stab_results = check_stabilizers(circuit_str, input_stabilizers)
                all_stabilized = all(stab_results.values())
            except Exception as e:
                print(f"  ⚠ Error checking stabilizers for circuit in '{code_name}': {e}")
                all_stabilized = None

            circuit_entry["all_stabilized"] = all_stabilized
            updated += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return updated

#%%
def process_one(filepath):
    stabilizers_map = load_benchmarks("../data/circuit_dataset.jsonl")
    process_outcome_file(filepath, stabilizers_map)

#%%
def main():
    parser = argparse.ArgumentParser(
        description="Add all_stabilized field to generated_circuits in outcome files"
    )
    parser.add_argument(
        "--benchmarks",
        default="../data/circuit_dataset.jsonl",
        help="Path to benchmarks JSONL file (default: ../data/circuit_dataset.jsonl)"
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Path to data directory containing model subdirectories (default: data)"
    )
    args = parser.parse_args()

    # Load benchmark stabilizers
    stabilizers_map = load_benchmarks(args.benchmarks)
    print(f"Loaded {len(stabilizers_map)} benchmarks from {args.benchmarks}")

    # Find all outcome JSON files in model subdirectories
    pattern = os.path.join(args.data_dir, "*", "*.json")
    outcome_files = sorted(glob.glob(pattern))
    print(f"Found {len(outcome_files)} outcome files\n")

    for filepath in outcome_files:
        print(f"Processing {filepath}...")
        updated = process_outcome_file(filepath, stabilizers_map)
        print(f"  ✓ Updated {updated} circuit entries\n")

    print("Done.")

#%%
if __name__ == "__main__":
    main()
