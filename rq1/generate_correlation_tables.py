import json
import pandas as pd
import argparse

def generate_correlation_tables(input_json,
                                 success_output_csv,
                                 runtime_output_csv):

    # Load JSON
    with open(input_json) as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    features = [
        "logical_qubits",
        "physical_qubits",
        "n_stabilizers",
        "distance",
        "total_gates",
        "weighted_gate_count",
        "avg_stabilizer_weight",
        "max_stabilizer_weight"
    ]

    target_columns = ["success_rate", "elapsed_seconds"]

    # Convert only relevant columns to numeric
    for col in features + target_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows where target values are missing
    df_success = df.dropna(subset=["success_rate"])
    df_runtime = df.dropna(subset=["elapsed_seconds"])

    # -------- SUCCESS CORRELATION --------
    success_corr_rows = []

    for feature in features:
        if feature in df_success.columns:
            temp_df = df_success.dropna(subset=[feature])
            corr = temp_df["success_rate"].corr(temp_df[feature])
            success_corr_rows.append({
                "feature": feature,
                "pearson_correlation": corr
            })

    success_df = pd.DataFrame(success_corr_rows)
    success_df.to_csv(success_output_csv, index=False)

    # -------- RUNTIME CORRELATION --------
    runtime_corr_rows = []

    for feature in features:
        if feature in df_runtime.columns:
            temp_df = df_runtime.dropna(subset=[feature])
            corr = temp_df["elapsed_seconds"].corr(temp_df[feature])
            runtime_corr_rows.append({
                "feature": feature,
                "pearson_correlation": corr
            })

    runtime_df = pd.DataFrame(runtime_corr_rows)
    runtime_df.to_csv(runtime_output_csv, index=False)

    print("Correlation tables written to:")
    print(success_output_csv)
    print(runtime_output_csv)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate correlation tables for success rate and runtime.")
    parser.add_argument("--input_json", type=str, required=True, help="Path to input JSON file with features and results.")
    parser.add_argument("--success_output_csv", type=str, default="success_rate_correlation.csv", help="Output CSV for success rate correlations.")
    parser.add_argument("--runtime_output_csv", type=str, default="runtime_correlation.csv", help="Output CSV for runtime correlations.")

    args = parser.parse_args()

    generate_correlation_tables(args.input_json, args.success_output_csv, args.runtime_output_csv)