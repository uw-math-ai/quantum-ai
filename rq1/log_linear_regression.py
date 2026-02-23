import json
import argparse
import numpy as np
import pandas as pd
import statsmodels.api as sm

def run_log_runtime_regression(input_json, output_path):
    # Load data
    with open(input_json, "r") as f:
        data = json.load(f)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Drop rows with missing runtime
    df = df.dropna(subset=["elapsed_seconds"])

    # Compute log of runtime
    df["log_runtime"] = np.log(df["elapsed_seconds"])

    # Features to include
    features = [
        "logical_qubits",
        "physical_qubits",
        "n_stabilizers",
        "distance",
        "total_gates",
        "weighted_gate_count",
        "avg_stabilizer_weight",
        "max_stabilizer_weight",
    ]

    # Drop rows with missing feature values
    df = df.dropna(subset=features)

    X = df[features]
    y = df["log_runtime"]

    # Add constant term for intercept
    X = sm.add_constant(X)

    # Fit linear regression
    model = sm.OLS(y, X).fit()

    # Write results to output file
    with open(output_path, "w") as f:
        f.write("===== LINEAR REGRESSION ON LOG(RUNTIME) =====\n")
        f.write(model.summary().as_text())

    print(f"Results written to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Linear regression on log(runtime)")
    parser.add_argument("input_json", type=str, help="Path to input JSON file")
    parser.add_argument("output_file", type=str, help="Path to output file for results")
    args = parser.parse_args()

    run_log_runtime_regression(args.input_json, args.output_file)