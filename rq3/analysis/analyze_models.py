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
def extract_stats(data: dict) -> dict:
    results = data.get("results", [])
    total = len(results)
    valid = sum(1 for r in results if r.get("valid", False))
    better = sum(1 for r in results if r.get("better", False))
    valid_and_better = sum(1 for r in results if r.get("valid") and r.get("better"))

    cx_reds, vol_reds, dep_reds = [], [], []
    success_with_opt_metrics = 0
    cx_reduced_success = 0
    twoq_reduced_success = 0
    swap_like_success = 0
    for r in results:
        if r.get("valid") and r.get("better"):
            bm, om = r.get("baseline_metrics", {}), r.get("optimized_metrics", {})
            if bm.get("cx_count", 0) > 0:
                cx_reds.append((bm["cx_count"] - om["cx_count"]) / bm["cx_count"] * 100)
            if bm.get("volume", 0) > 0:
                vol_reds.append((bm["volume"] - om["volume"]) / bm["volume"] * 100)
            if bm.get("depth", 0) > 0:
                dep_reds.append((bm["depth"] - om["depth"]) / bm["depth"] * 100)

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

    return {
        "total": total,
        "valid": valid,
        "better": better,
        "valid_and_better": valid_and_better,
        "valid_rate": valid / total * 100 if total else 0,
        "better_rate": better / total * 100 if total else 0,
        "success_rate": valid_and_better / total * 100 if total else 0,
        "mean_cx_red": np.mean(cx_reds) if cx_reds else 0,
        "mean_vol_red": np.mean(vol_reds) if vol_reds else 0,
        "mean_dep_red": np.mean(dep_reds) if dep_reds else 0,
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
def discover(data_dir: str) -> dict:
    """Returns {model_name: {config_label: stats_dict}}"""
    all_data = {}
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
                f"2q_red|succ={stats['twoq_reduced_within_success_rate']:5.1f}%  "
                f"swap_like|succ={stats['swap_like_within_success_rate']:5.1f}%")

        all_data[model_name] = configs
    return all_data


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

    fig, axes = plt.subplots(3, 2, figsize=(14, 13))
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
                 "Mean CX-Count Reduction", "Reduction (%)")
    grouped_bars(axes[1, 1], "mean_dep_red",
                 "Mean Depth Reduction", "Reduction (%)")
    grouped_bars(axes[2, 0], "twoq_reduced_within_success_rate",
                 "True 2Q Reduction (among successes)", "Rate (%)")
    grouped_bars(axes[2, 1], "swap_like_within_success_rate",
                 "CX↓ but 2Q not↓ (among successes)", "Rate (%)")

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
    all_data = discover(data_dir)

    if not all_data:
        print("No model data found.")
        sys.exit(1)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_comparison.png")
    plot_all(all_data, output_path)


if __name__ == "__main__":
    main()