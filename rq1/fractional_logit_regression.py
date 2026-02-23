import json
import argparse
import pandas as pd
import statsmodels.api as sm


FEATURE_COLUMNS = [
    "logical_qubits",
    "physical_qubits",
    "n_stabilizers",
    "distance",
    "total_gates",
    "weighted_gate_count",
    "avg_stabilizer_weight",
    "max_stabilizer_weight",
]


def run_fractional_logit(input_json_path, output_path):
    # ----------------------------
    # Load data
    # ----------------------------
    with open(input_json_path, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Convert to numeric safely
    df = df.apply(pd.to_numeric, errors="coerce")

    # Drop missing rows
    df = df.dropna(subset=["success_rate"] + FEATURE_COLUMNS)

    y = df["success_rate"]
    X = df[FEATURE_COLUMNS]

    # Add intercept
    X = sm.add_constant(X)

    # ----------------------------
    # Fractional Logit Model
    # ----------------------------
    model = sm.GLM(
        y,
        X,
        family=sm.families.Binomial(link=sm.families.links.logit())
    )

    results = model.fit(cov_type="HC3")  # robust standard errors

    # Pseudo R-squared (McFadden)
    llf = results.llf
    llnull = results.null_deviance / -2
    pseudo_r2 = 1 - (llf / llnull)

    # Write results to output file
    with open(output_path, "w") as f:
        f.write("\n===== FRACTIONAL LOGIT RESULTS =====\n\n")
        f.write(results.summary().as_text())
        f.write(f"\n\nMcFadden Pseudo R-squared: {pseudo_r2:.4f}\n")

    print(f"Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run fractional logit regression on success_rate."
    )
    parser.add_argument("input_json", help="Path to input JSON file")
    parser.add_argument("output_file", help="Path to output file for results")
    args = parser.parse_args()

    run_fractional_logit(args.input_json, args.output_file)