"""
Gate-swap quality check for RQ3 experiments.

Purpose:
- Distinguish true multi-qubit improvement from CX-to-other-2Q swaps.
- Report how often CX reduction also reduces total two-qubit operations.

Usage:
    python gate_swap_stats.py <data_directory>
Example:
    python gate_swap_stats.py data
"""

import glob
import json
import os
import sys
from collections import defaultdict


def classify_config(meta: dict) -> str:
    attempts = meta.get("max_attempts", 1)
    timeout = meta.get("timeout", 0)
    if attempts == 1:
        return "1 attempt"
    if attempts == 15 and timeout <= 300:
        return "15 att / 300s"
    if attempts == 15:
        return f"15 att / {timeout}s"
    return f"{attempts} att / {timeout}s"


def extract_rows(data_dir: str) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(glob.glob(os.path.join(data_dir, "*", "*.json"))):
        with open(path) as f:
            data = json.load(f)

        model = os.path.basename(os.path.dirname(path))
        cfg = classify_config(data.get("metadata", {}))

        for r in data.get("results", []):
            bm = r.get("baseline_metrics") or {}
            om = r.get("optimized_metrics") or {}
            success = bool(r.get("valid")) and bool(r.get("better"))
            has_opt = bool(om)

            has_cx_pair = "cx_count" in bm and "cx_count" in om
            has_twoq_pair = "two_qubit_gates" in bm and "two_qubit_gates" in om

            cx_reduced = has_cx_pair and om["cx_count"] < bm["cx_count"]
            twoq_reduced = has_twoq_pair and om["two_qubit_gates"] < bm["two_qubit_gates"]

            rows.append(
                {
                    "model": model,
                    "cfg": cfg,
                    "success": success,
                    "has_opt": has_opt,
                    "cx_reduced": cx_reduced,
                    "twoq_reduced": twoq_reduced,
                    "swap_like": cx_reduced and (not twoq_reduced),
                }
            )

    return rows


def pct(numer: int, denom: int) -> float:
    return (numer / denom * 100) if denom else 0.0


def print_report(rows: list[dict]) -> None:
    total = len(rows)
    success_total = sum(1 for x in rows if x["success"])
    success_with_opt = [x for x in rows if x["success"] and x["has_opt"]]

    cx_reduced = sum(1 for x in success_with_opt if x["cx_reduced"])
    twoq_reduced = sum(1 for x in success_with_opt if x["twoq_reduced"])
    swap_like = sum(1 for x in success_with_opt if x["swap_like"])

    print(f"TOTAL_ROWS={total}")
    print(f"TOTAL_SUCCESS={success_total}")
    print(f"SUCCESS_WITH_OPT_METRICS={len(success_with_opt)}")
    print(
        "POOLED|"
        f"cx_reduced_within_success={pct(cx_reduced, len(success_with_opt)):.1f}%|"
        f"twoq_reduced_within_success={pct(twoq_reduced, len(success_with_opt)):.1f}%|"
        f"swap_like_within_success={pct(swap_like, len(success_with_opt)):.1f}%"
    )

    by_group: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for x in rows:
        by_group[(x["model"], x["cfg"])].append(x)

    print("\nBY_MODEL_CONFIG")
    for (model, cfg), group in sorted(by_group.items()):
        sopt = [x for x in group if x["success"] and x["has_opt"]]
        n = len(sopt)
        if n == 0:
            print(f"{model}|{cfg}|n=0")
            continue

        c = sum(1 for x in sopt if x["cx_reduced"])
        t = sum(1 for x in sopt if x["twoq_reduced"])
        s = sum(1 for x in sopt if x["swap_like"])
        print(
            f"{model}|{cfg}|n={n}|"
            f"cx_reduced={pct(c, n):.1f}%|"
            f"twoq_reduced={pct(t, n):.1f}%|"
            f"swap_like={pct(s, n):.1f}%"
        )


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python gate_swap_stats.py <data_directory>")
        sys.exit(1)

    data_dir = sys.argv[1]
    rows = extract_rows(data_dir)
    if not rows:
        print("No rows found.")
        sys.exit(1)

    print_report(rows)


if __name__ == "__main__":
    main()
