"""
Circuit Optimization — Multi-Model × Multi-Config Comparison
--------------------------------------------------------------
Walks a directory tree like:
    data/
      claude-opus-4.6/
        260304.1021.json   (max_attempts=1)
        260305.1116.json   (max_attempts=15, timeout=300)
        260306.1001.json   (max_attempts=15, timeout=900)
      gpt5.2/
        ...

Config type is inferred from metadata.max_attempts + metadata.timeout.

Usage:
    python analyze_models.py <data_directory>
"""

import json, sys, os, glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Config classification ────────────────────────────────────────────
def classify_config(meta: dict) -> str:
    attempts = meta.get("max_attempts", 1)
    timeout = meta.get("timeout", 0)
    if attempts == 1:
        return "1 attempt"
    elif attempts == 15 and timeout <= 300:
        return "15 att / 300s"
    elif attempts == 15 and timeout > 300:
        return f"15 att / {timeout}s"
    else:
        return f"{attempts} att / {timeout}s"

CONFIG_ORDER = ["1 attempt", "15 att / 300s", "15 att / 900s"]

# ── Stat extraction ──────────────────────────────────────────────────
def improvement_magnitude(bm: dict, om: dict) -> float:
    """
    Return the reduction % for whichever metric triggered the lexicographic
    is_better check: CX first, then volume, then depth.  Mirrors the runner's
        (cx, volume, depth) < (cx, volume, depth)
    """
    cx_b, cx_o = bm.get("cx_count", 0), om.get("cx_count", 0)
    vol_b, vol_o = bm.get("volume", 0), om.get("volume", 0)
    dep_b, dep_o = bm.get("depth", 0), om.get("depth", 0)

    if cx_o < cx_b and cx_b > 0:
        return (cx_b - cx_o) / cx_b * 100
    elif cx_o == cx_b and vol_o < vol_b and vol_b > 0:
        return (vol_b - vol_o) / vol_b * 100
    elif cx_o == cx_b and vol_o == vol_b and dep_o < dep_b and dep_b > 0:
        return (dep_b - dep_o) / dep_b * 100
    return 0.0


def extract_stats(data: dict) -> dict:
    results = data.get("results", [])
    total = len(results)
    valid = sum(1 for r in results if r.get("valid", False))
    better = sum(1 for r in results if r.get("better", False))
    valid_and_better = sum(1 for r in results if r.get("valid") and r.get("better"))

    # --- Among successes ---
    cx_reds, vol_reds, dep_reds = [], [], []
    success_with_opt_metrics = 0
    cx_reduced_success = 0
    twoq_reduced_success = 0
    swap_like_success = 0

    # --- Over ALL circuits (failures = 0%) ---
    cx_reds_all = []
    dep_reds_all = []
    improvement_mags_all = []  # lexicographic improvement magnitude

    for r in results:
        bm = r.get("baseline_metrics", {})
        om = r.get("optimized_metrics", {})
        is_success = r.get("valid") and r.get("better")

        if is_success:
            # Among-successes metrics (unchanged)
            if bm.get("cx_count", 0) > 0:
                cx_red = (bm["cx_count"] - om["cx_count"]) / bm["cx_count"] * 100
                cx_reds.append(cx_red)
            if bm.get("volume", 0) > 0:
                vol_reds.append((bm["volume"] - om["volume"]) / bm["volume"] * 100)
            if bm.get("depth", 0) > 0:
                dep_red = (bm["depth"] - om["depth"]) / bm["depth"] * 100
                dep_reds.append(dep_red)

            if om:
                success_with_opt_metrics += 1
                has_cx = "cx_count" in bm and "cx_count" in om
                has_twoq = "two_qubit_gates" in bm and "two_qubit_gates" in om

                cx_reduced = has_cx and om["cx_count"] < bm["cx_count"]
                twoq_reduced = has_twoq and om["two_qubit_gates"] < bm["two_qubit_gates"]

                if cx_reduced:
                    cx_reduced_success += 1
                if twoq_reduced:
                    twoq_reduced_success += 1
                if cx_reduced and not twoq_reduced:
                    swap_like_success += 1

            # Over-all CX and depth (for diagnostic charts)
            if bm.get("cx_count", 0) > 0:
                cx_reds_all.append(
                    (bm["cx_count"] - om.get("cx_count", bm["cx_count"])) / bm["cx_count"] * 100
                )
            else:
                cx_reds_all.append(0.0)

            if bm.get("depth", 0) > 0:
                dep_reds_all.append(
                    (bm["depth"] - om.get("depth", bm["depth"])) / bm["depth"] * 100
                )
            else:
                dep_reds_all.append(0.0)

            # Improvement magnitude (matches lexicographic is_better)
            improvement_mags_all.append(improvement_magnitude(bm, om))
        else:
            # Failures count as 0%
            cx_reds_all.append(0.0)
            dep_reds_all.append(0.0)
            improvement_mags_all.append(0.0)

    success_rate = valid_and_better / total * 100 if total else 0
    mean_cx_red_all = np.mean(cx_reds_all) if cx_reds_all else 0
    mean_dep_red_all = np.mean(dep_reds_all) if dep_reds_all else 0
    mean_improvement_all = np.mean(improvement_mags_all) if improvement_mags_all else 0

    # Benchmark score: 0.50 * success_rate + 0.50 * mean_improvement_all
    score = 0.50 * success_rate + 0.50 * mean_improvement_all

    return {
        "total": total,
        "valid": valid,
        "better": better,
        "valid_and_better": valid_and_better,
        "valid_rate": valid / total * 100 if total else 0,
        "better_rate": better / total * 100 if total else 0,
        "success_rate": success_rate,
        # Among successes
        "mean_cx_red": np.mean(cx_reds) if cx_reds else 0,
        "mean_vol_red": np.mean(vol_reds) if vol_reds else 0,
        "mean_dep_red": np.mean(dep_reds) if dep_reds else 0,
        # Over ALL circuits (failures = 0%)
        "mean_cx_red_all": mean_cx_red_all,
        "mean_dep_red_all": mean_dep_red_all,
        "mean_improvement_all": mean_improvement_all,
        # Benchmark score
        "score": score,
        # 2Q quality
        "success_with_opt_metrics": success_with_opt_metrics,
        "cx_reduced_within_success_rate": (
            cx_reduced_success / success_with_opt_metrics * 100 if success_with_opt_metrics else 0
        ),
        "twoq_reduced_within_success_rate": (
            twoq_reduced_success / success_with_opt_metrics * 100 if success_with_opt_metrics else 0
        ),
        "swap_like_within_success_rate": (
            swap_like_success / success_with_opt_metrics * 100 if success_with_opt_metrics else 0
        ),
    }


# ── Discovery ────────────────────────────────────────────────────────
def discover(data_dir: str) -> tuple[dict, list[dict]]:
    """Returns ({model_name: {config_label: stats_dict}}, [raw_rows])"""
    all_data = {}
    all_rows = []  # flat list of per-circuit rows for bucket analysis

    for model_dir in sorted(glob.glob(os.path.join(data_dir, "*"))):
        if not os.path.isdir(model_dir):
            continue
        model_name = os.path.basename(model_dir)
        if model_name in ("agent_files",):
            continue

        # ── Only analyze these models ──
        MODELS_TO_ANALYZE = {"claude-opus-4.6", "gpt5.2"}
        if model_name not in MODELS_TO_ANALYZE:
            continue

        json_files = sorted(glob.glob(os.path.join(model_dir, "*.json")))
        if not json_files:
            continue

        configs = {}
        for jf in json_files:
            with open(jf) as f:
                data = json.load(f)
            meta = data.get("metadata", {})
            cfg = classify_config(meta)
            stats = extract_stats(data)
            configs[cfg] = stats
            print(f"  {model_name:25s}  {cfg:16s}  n={stats['total']:3d}  "
                  f"success={stats['success_rate']:5.1f}%  "
                  f"cx_red={stats['mean_cx_red']:5.1f}%  "
                  f"cx_red_all={stats['mean_cx_red_all']:5.1f}%  "
                  f"imp_all={stats['mean_improvement_all']:5.1f}%  "
                  f"SCORE={stats['score']:5.1f}  "
                  f"2q_red|succ={stats['twoq_reduced_within_success_rate']:5.1f}%  "
                  f"swap_like|succ={stats['swap_like_within_success_rate']:5.1f}%")

            # Collect raw rows for bucket analysis
            for r in data.get("results", []):
                bm = r.get("baseline_metrics", {})
                all_rows.append({
                    "model": model_name,
                    "cfg": cfg,
                    "success": bool(r.get("valid")) and bool(r.get("better")),
                    "cx_count": bm.get("cx_count"),
                    "depth": bm.get("depth"),
                })

        all_data[model_name] = configs
    return all_data, all_rows


# ── Circuit-size bucket analysis ─────────────────────────────────────
def print_bucket_analysis(all_rows: list[dict]):
    """Compute CX-count quartiles and report success by size bucket."""
    cx_vals = sorted([r["cx_count"] for r in all_rows
                      if isinstance(r["cx_count"], (int, float))])
    if not cx_vals:
        print("\nNo CX count data for bucket analysis.")
        return

    q1 = cx_vals[len(cx_vals) // 4]
    q2 = cx_vals[len(cx_vals) // 2]
    q3 = cx_vals[(3 * len(cx_vals)) // 4]

    def cx_bin(v):
        if v is None:
            return "unknown"
        if v <= q1:
            return "Small"
        if v <= q2:
            return "Medium"
        if v <= q3:
            return "Large"
        return "Extra-large"

    print("\n" + "=" * 80)
    print("  CIRCUIT-SIZE BUCKET ANALYSIS")
    print(f"  CX-count quartile cutoffs: Q1={q1}, Q2(median)={q2}, Q3={q3}")
    print(f"  Small: CX ≤ {q1}  |  Medium: {q1} < CX ≤ {q2}  |  "
          f"Large: {q2} < CX ≤ {q3}  |  Extra-large: CX > {q3}")
    print("=" * 80)

    # ── Pooled across all models/configs ──
    from collections import defaultdict
    pooled = defaultdict(list)
    for r in all_rows:
        pooled[cx_bin(r["cx_count"])].append(r)

    print(f"\n  {'Bucket':<14s}  {'CX range':<20s}  {'n':>5s}  {'Success':>8s}  {'Rate':>7s}")
    print("-" * 65)
    for bucket in ["Small", "Medium", "Large", "Extra-large"]:
        rows = pooled.get(bucket, [])
        n = len(rows)
        succ = sum(1 for r in rows if r["success"])
        rate = succ / n * 100 if n else 0
        if bucket == "Small":
            rng = f"CX ≤ {q1}"
        elif bucket == "Medium":
            rng = f"{q1} < CX ≤ {q2}"
        elif bucket == "Large":
            rng = f"{q2} < CX ≤ {q3}"
        else:
            rng = f"CX > {q3}"
        print(f"  {bucket:<14s}  {rng:<20s}  {n:5d}  {succ:8d}  {rate:6.1f}%")

    # ── Per model, pooled across configs ──
    print(f"\n  {'Model':<25s}  {'Bucket':<14s}  {'n':>5s}  {'Success':>8s}  {'Rate':>7s}")
    print("-" * 70)
    by_model_bucket = defaultdict(lambda: defaultdict(list))
    for r in all_rows:
        by_model_bucket[r["model"]][cx_bin(r["cx_count"])].append(r)

    for model in sorted(by_model_bucket):
        for bucket in ["Small", "Medium", "Large", "Extra-large"]:
            rows = by_model_bucket[model].get(bucket, [])
            n = len(rows)
            succ = sum(1 for r in rows if r["success"])
            rate = succ / n * 100 if n else 0
            print(f"  {model:<25s}  {bucket:<14s}  {n:5d}  {succ:8d}  {rate:6.1f}%")

    # ── Per config, pooled across models ──
    print(f"\n  {'Config':<16s}  {'Bucket':<14s}  {'n':>5s}  {'Success':>8s}  {'Rate':>7s}")
    print("-" * 65)
    by_cfg_bucket = defaultdict(lambda: defaultdict(list))
    for r in all_rows:
        by_cfg_bucket[r["cfg"]][cx_bin(r["cx_count"])].append(r)

    for cfg in CONFIG_ORDER:
        if cfg not in by_cfg_bucket:
            continue
        for bucket in ["Small", "Medium", "Large", "Extra-large"]:
            rows = by_cfg_bucket[cfg].get(bucket, [])
            n = len(rows)
            succ = sum(1 for r in rows if r["success"])
            rate = succ / n * 100 if n else 0
            print(f"  {cfg:<16s}  {bucket:<14s}  {n:5d}  {succ:8d}  {rate:6.1f}%")

    print("=" * 80)


# ── Score summary ────────────────────────────────────────────────────
def print_score_summary(all_data: dict):
    """Print a clean benchmark score summary table."""
    print("\n" + "=" * 80)
    print("  RQ3 BENCHMARK SCORES")
    print("  Score = 0.50 × SuccessRate + 0.50 × MeanImprovementMagnitude(all)")
    print("  Improvement magnitude: CX red % if CX↓, else Vol red % if Vol↓, else Dep red %")
    print("=" * 80)
    print(f"  {'Model':<25s}  {'Config':<16s}  {'Success':>8s}  {'CX↓(succ)':>10s}  "
          f"{'CX↓(all)':>9s}  {'Imp(all)':>9s}  {'SCORE':>6s}")
    print("-" * 80)
    for model in sorted(all_data.keys()):
        for cfg in CONFIG_ORDER:
            s = all_data[model].get(cfg)
            if s is None:
                continue
            print(f"  {model:<25s}  {cfg:<16s}  {s['success_rate']:7.1f}%  "
                  f"{s['mean_cx_red']:9.1f}%  "
                  f"{s['mean_cx_red_all']:8.1f}%  "
                  f"{s['mean_improvement_all']:8.1f}%  "
                  f"{s['score']:6.1f}")
    print("=" * 80)


# ── Plotting ─────────────────────────────────────────────────────────
COLORS = {
    "1 attempt":      "#4C72B0",
    "15 att / 300s":  "#DD8452",
    "15 att / 900s":  "#55A868",
}

def plot_all(all_data: dict, output: str):
    models = list(all_data.keys())
    # Collect all configs that actually appear, sorted by CONFIG_ORDER
    seen_configs = sorted(
        {cfg for m in all_data.values() for cfg in m},
        key=lambda c: CONFIG_ORDER.index(c) if c in CONFIG_ORDER else 99
    )
    n_models = len(models)
    n_configs = len(seen_configs)

    fig, axes = plt.subplots(4, 2, figsize=(14, 17))
    fig.suptitle("Circuit Optimization — Model × Config Comparison",
                 fontsize=15, fontweight="bold")

    bar_width = 0.8 / max(n_configs, 1)
    x = np.arange(n_models)

    def grouped_bars(ax, metric_key, title, ylabel, fmt="{:.0f}%", is_pct=True):
        for i, cfg in enumerate(seen_configs):
            vals = []
            for m in models:
                s = all_data[m].get(cfg)
                vals.append(s[metric_key] if s else 0)
            offset = (i - (n_configs - 1) / 2) * bar_width
            bars = ax.bar(x + offset, vals, bar_width,
                          label=cfg, color=COLORS.get(cfg, f"C{i}"),
                          edgecolor="white", linewidth=0.5)
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, h + 0.8,
                            fmt.format(h), ha="center", va="bottom", fontsize=7)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=25, ha="right", fontsize=9)
        if is_pct:
            ax.set_ylim(0, max(ax.get_ylim()[1], 110))
            ax.yaxis.set_major_formatter(mticker.PercentFormatter())
        ax.legend(fontsize=8, loc="upper left")
        ax.grid(axis="y", alpha=0.3)

    grouped_bars(axes[0, 0], "success_rate",
                 "Success Rate (Valid & Better)", "Rate (%)")
    grouped_bars(axes[0, 1], "valid_rate",
                 "Validity Rate", "Rate (%)")
    grouped_bars(axes[1, 0], "mean_cx_red",
                 "Mean CX Reduction (among successes)", "Reduction (%)")
    grouped_bars(axes[1, 1], "mean_dep_red",
                 "Mean Depth Reduction (among successes)", "Reduction (%)")
    grouped_bars(axes[2, 0], "mean_cx_red_all",
                 "Mean CX Reduction (over all circuits)", "Reduction (%)")
    grouped_bars(axes[2, 1], "mean_improvement_all",
                 "Mean Improvement Magnitude (over all circuits)", "Reduction (%)")

    # Score plot (not percentage — raw 0-100 score)
    grouped_bars(axes[3, 0], "score",
                 "RQ3 Benchmark Score", "Score (0–100)", fmt="{:.1f}", is_pct=False)
    axes[3, 0].set_ylim(0, 100)
    axes[3, 0].axhline(y=50, color="gray", linestyle="--", alpha=0.3)

    # 2Q quality in remaining slot
    grouped_bars(axes[3, 1], "twoq_reduced_within_success_rate",
                 "True 2Q Reduction (among successes)", "Rate (%)")

    plt.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    print(f"\n✓ Chart saved to {output}")


# ── Main ─────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_models.py <data_directory>")
        sys.exit(1)

    data_dir = sys.argv[1]
    print(f"Scanning {data_dir} ...\n")
    all_data, all_rows = discover(data_dir)

    if not all_data:
        print("No model data found.")
        sys.exit(1)

    print_score_summary(all_data)
    print_bucket_analysis(all_rows)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_comparison.png")
    plot_all(all_data, output_path)


if __name__ == "__main__":
    main()