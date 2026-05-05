"""
Circuit Optimization — Multi-Model × Multi-Config Comparison
--------------------------------------------------------------
Configure which JSON result files to analyze per model in the
ANALYSIS_CONFIG dict below. Each entry maps a model name to a
list of result JSON filenames found under data/<model>/.

Usage:
    python analyze_models.py <data_directory>

Scores:
    Capability Score = Σ I(valid & better) × num_stabilizers
        → max ≈ 16k (sum of all stabilizer counts)

    Quality Score = Σ I(valid & better) × num_stabilizers × optimization_proportion
        where optimization_proportion =
            0.75 × (baseline_2Q - opt_2Q) / baseline_2Q
          + 0.25 × (baseline_dep - opt_dep) / baseline_dep
        (clamped to [0, 1] per metric; 0 if baseline metric is 0)
"""

import json, sys, os, glob
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ═══════════════════════════════════════════════════════════════════════
# CONFIGURE WHICH FILES TO ANALYZE HERE
# ═══════════════════════════════════════════════════════════════════════
ANALYSIS_CONFIG = {
    "claude-opus-4.6": [
        "260304.1021.json",     # 1 attempt
        "260305.1116.json",     # 15 att / 300s
        "260306.1001.json",     # 15 att / 900s
    ],
    "gpt5.2": [
        "260304.1023.json",
        "260305.1116.json",
        "260306.1001.json",
    ],
    "gemini-3-pro-preview": [
        "260304.1022.json",
    ],
}
# ═══════════════════════════════════════════════════════════════════════


# ── Dataset loader ───────────────────────────────────────────────────
def load_stabilizer_counts(data_dir: str) -> dict[str, int]:
    """Return {code_name: num_stabilizers} from circuit_dataset.jsonl."""
    candidates = [
        os.path.join(data_dir, "..", "data", "circuit_dataset.jsonl"),
        os.path.join(data_dir, "..", "..", "data", "circuit_dataset.jsonl"),
        os.path.join(data_dir, "circuit_dataset.jsonl"),
    ]
    for path in candidates:
        path = os.path.normpath(path)
        if os.path.exists(path):
            counts = {}
            with open(path) as f:
                for line in f:
                    rec = json.loads(line)
                    name = rec.get("source_code", "")
                    stabs = rec.get("input_stabilizers", [])
                    if name and stabs:
                        counts[name] = len(stabs)
            return counts
    return {}


# ── Config classification (read from metadata) ──────────────────────
def classify_config(meta: dict) -> str:
    attempts = meta.get("max_attempts", 1)
    timeout = meta.get("timeout", 0)
    if attempts == 1:
        return "1 attempt"
    return f"{attempts} att / {timeout}s"


# ── Optimization proportion ─────────────────────────────────────────
def optimization_proportion(bm: dict, om: dict) -> float:
    """
    Weighted proportion of improvement across 2 metrics.
    0.75 × 2Q reduction + 0.25 × depth reduction
    Each metric proportion is clamped to [0, 1].
    """
    def metric_prop(baseline_val, opt_val):
        if baseline_val <= 0:
            return 0.0
        prop = (baseline_val - opt_val) / baseline_val
        return max(0.0, min(1.0, prop))

    twoq_b = bm.get("two_qubit_gates", bm.get("cx_count", 0))
    twoq_o = om.get("two_qubit_gates", om.get("cx_count", twoq_b))
    dep_b = bm.get("depth", 0)
    dep_o = om.get("depth", dep_b)

    return (
        0.75 * metric_prop(twoq_b, twoq_o)
        + 0.25 * metric_prop(dep_b, dep_o)
    )


# ── Stat extraction ──────────────────────────────────────────────────
def improvement_magnitude(bm: dict, om: dict) -> float:
    """2Q-gate reduction % if 2Q improved, else volume, else depth."""
    twoq_b = bm.get("two_qubit_gates", bm.get("cx_count", 0))
    twoq_o = om.get("two_qubit_gates", om.get("cx_count", 0))
    vol_b, vol_o = bm.get("volume", 0), om.get("volume", 0)
    dep_b, dep_o = bm.get("depth", 0), om.get("depth", 0)
    if twoq_o < twoq_b and twoq_b > 0:
        return (twoq_b - twoq_o) / twoq_b * 100
    elif twoq_o == twoq_b and vol_o < vol_b and vol_b > 0:
        return (vol_b - vol_o) / vol_b * 100
    elif twoq_o == twoq_b and vol_o == vol_b and dep_o < dep_b and dep_b > 0:
        return (dep_b - dep_o) / dep_b * 100
    return 0.0


def extract_stats(data: dict, stab_counts: dict = None) -> dict:
    results = data.get("results", [])
    total = len(results)
    valid_and_better = sum(1 for r in results if r.get("valid") and r.get("better"))

    cx_reds, dep_reds = [], []
    twoq_reduced_success = 0
    success_with_opt_metrics = 0
    cx_reds_all, improvement_mags_all = [], []

    # Metric improvement breakdown
    all3_improved = 0
    twoq_vol_improved = 0
    twoq_dep_improved = 0
    twoq_only_improved = 0
    vol_dep_improved = 0
    vol_only_improved = 0
    dep_only_improved = 0

    for r in results:
        bm = r.get("baseline_metrics", {})
        om = r.get("optimized_metrics", {})
        is_success = r.get("valid") and r.get("better")

        if is_success:
            if bm.get("cx_count", 0) > 0:
                cx_reds.append((bm["cx_count"] - om["cx_count"]) / bm["cx_count"] * 100)
            if bm.get("depth", 0) > 0:
                dep_reds.append((bm["depth"] - om["depth"]) / bm["depth"] * 100)
            if om:
                success_with_opt_metrics += 1
                if ("two_qubit_gates" in bm and "two_qubit_gates" in om
                        and om["two_qubit_gates"] < bm["two_qubit_gates"]):
                    twoq_reduced_success += 1
            cx_reds_all.append(
                (bm["cx_count"] - om.get("cx_count", bm["cx_count"])) / bm["cx_count"] * 100
                if bm.get("cx_count", 0) > 0 else 0.0
            )
            improvement_mags_all.append(improvement_magnitude(bm, om))

            twoq_b = bm.get("two_qubit_gates", bm.get("cx_count", 0))
            twoq_o = om.get("two_qubit_gates", om.get("cx_count", twoq_b))
            vol_b = bm.get("volume", 0)
            vol_o = om.get("volume", vol_b)
            dep_b = bm.get("depth", 0)
            dep_o = om.get("depth", dep_b)

            twoq_imp = twoq_o < twoq_b
            vol_imp = vol_o < vol_b
            dep_imp = dep_o < dep_b

            if twoq_imp and vol_imp and dep_imp:
                all3_improved += 1
            elif twoq_imp and vol_imp:
                twoq_vol_improved += 1
            elif twoq_imp and dep_imp:
                twoq_dep_improved += 1
            elif twoq_imp:
                twoq_only_improved += 1
            elif vol_imp and dep_imp:
                vol_dep_improved += 1
            elif vol_imp:
                vol_only_improved += 1
            else:
                dep_only_improved += 1
        else:
            cx_reds_all.append(0.0)
            improvement_mags_all.append(0.0)

    success_rate = valid_and_better / total * 100 if total else 0
    mean_improvement_all = np.mean(improvement_mags_all) if improvement_mags_all else 0
    score = 0.50 * success_rate + 0.50 * mean_improvement_all

    # Capability score: I(valid & better) × num_stabilizers
    capability_score = 0
    max_capability_score = 0
    # Quality score: capability × optimization_proportion
    quality_score = 0.0

    if stab_counts:
        for r in results:
            code_name = r.get("code_name", "")
            n_stab = stab_counts.get(code_name, 0)
            max_capability_score += n_stab
            if r.get("valid") and r.get("better"):
                capability_score += n_stab
                bm = r.get("baseline_metrics", {})
                om = r.get("optimized_metrics", {})
                opt_prop = optimization_proportion(bm, om)
                quality_score += n_stab * opt_prop

    return {
        "total": total,
        "valid_and_better": valid_and_better,
        "valid_rate": sum(1 for r in results if r.get("valid")) / total * 100 if total else 0,
        "success_rate": success_rate,
        "mean_cx_red": np.mean(cx_reds) if cx_reds else 0,
        "mean_dep_red": np.mean(dep_reds) if dep_reds else 0,
        "mean_cx_red_all": np.mean(cx_reds_all) if cx_reds_all else 0,
        "mean_improvement_all": mean_improvement_all,
        "score": score,
        "capability_score": capability_score,
        "max_capability_score": max_capability_score,
        "quality_score": quality_score,
        "twoq_reduced_within_success_rate": (
            twoq_reduced_success / success_with_opt_metrics * 100
            if success_with_opt_metrics else 0
        ),
        "all3_improved": all3_improved,
        "twoq_vol_improved": twoq_vol_improved,
        "twoq_dep_improved": twoq_dep_improved,
        "twoq_only_improved": twoq_only_improved,
        "vol_dep_improved": vol_dep_improved,
        "vol_only_improved": vol_only_improved,
        "dep_only_improved": dep_only_improved,
    }


# ── Discovery (uses ANALYSIS_CONFIG) ────────────────────────────────
def discover(data_dir: str) -> tuple[dict, list[dict], list[str]]:
    """Returns ({model: {config: stats}}, [raw_rows], [config_labels_seen])"""
    stab_counts = load_stabilizer_counts(data_dir)
    if stab_counts:
        print(f"  Loaded stabilizer counts for {len(stab_counts)} circuits.\n")
    else:
        print("  Warning: could not load circuit_dataset.jsonl — stabilizer analysis unavailable.\n")

    all_data = {}
    all_rows = []
    configs_seen = []

    for model_name, json_files in sorted(ANALYSIS_CONFIG.items()):
        if not json_files:
            continue

        configs = {}
        for jf in json_files:
            full_path = os.path.join(data_dir, model_name, jf)
            if not os.path.exists(full_path):
                print(f"  ⚠ File not found: {full_path}")
                continue

            with open(full_path) as f:
                data = json.load(f)

            meta = data.get("metadata", {})
            cfg = classify_config(meta)
            if cfg not in configs_seen:
                configs_seen.append(cfg)

            stats = extract_stats(data, stab_counts)
            configs[cfg] = stats

            cap = stats["capability_score"]
            cap_max = stats["max_capability_score"]
            qual = stats["quality_score"]
            print(f"  {model_name:25s}  {cfg:16s}  [{jf}]  n={stats['total']:3d}  "
                  f"success={stats['success_rate']:5.1f}%  "
                  f"capability={cap:,}/{cap_max:,}  "
                  f"quality={qual:,.1f}")

            for r in data.get("results", []):
                bm = r.get("baseline_metrics", {})
                code_name = r.get("code_name", "")
                all_rows.append({
                    "model": model_name,
                    "cfg": cfg,
                    "success": bool(r.get("valid")) and bool(r.get("better")),
                    "cx_count": bm.get("cx_count"),
                    "num_stabilizers": stab_counts.get(code_name),
                    "code_name": code_name,
                })

        if configs:
            all_data[model_name] = configs

    return all_data, all_rows, configs_seen


# ── Score summary ────────────────────────────────────────────────────
def print_score_summary(all_data: dict, configs_seen: list[str]):
    print("\n" + "=" * 140)
    print("  RQ3 BENCHMARK SCORES")
    print("  Capability Score = Σ I(valid & better) × num_stabilizers")
    print("  Quality Score    = Σ I(valid & better) × num_stabilizers × optimization_proportion")
    print("     optimization_proportion = 0.75×(2Q↓%) + 0.25×(dep↓%)")
    print("=" * 140)
    print(f"  {'Model':<25s}  {'Config':<16s}  {'Success':>8s}  {'CX↓(succ)':>10s}  "
          f"{'Imp(all)':>9s}  {'Capability':>20s}  {'Quality':>12s}")
    print("-" * 140)
    for model in sorted(all_data.keys()):
        for cfg in configs_seen:
            s = all_data[model].get(cfg)
            if s is None:
                continue
            cap = s["capability_score"]
            cap_max = s["max_capability_score"]
            cap_str = f"{cap:,} / {cap_max:,}" if cap_max else "N/A"
            qual_str = f"{s['quality_score']:,.1f}"
            print(f"  {model:<25s}  {cfg:<16s}  {s['success_rate']:7.1f}%  "
                  f"{s['mean_cx_red']:9.1f}%  "
                  f"{s['mean_improvement_all']:8.1f}%  "
                  f"{cap_str:>20s}  "
                  f"{qual_str:>12s}")
    print("=" * 140)


# ── Metric improvement breakdown ────────────────────────────────────
def print_metric_breakdown(all_data: dict, configs_seen: list[str]):
    total_circuits = next(
        (s["total"] for m in all_data.values() for s in m.values()), 192
    )
    print("\n" + "=" * 125)
    print("  METRIC IMPROVEMENT BREAKDOWN  (among valid & better circuits)")
    print(f"  Denominator = total circuits per run ({total_circuits})")
    print("  2Q = two-qubit gates (CX/CZ/SWAP),  Vol = total gate count,  Dep = circuit depth")
    print("=" * 125)
    print(f"  {'Model':<25s}  {'Config':<16s}  {'Successes':>9s}  "
          f"{'2Q+Vol+Dep':>11s}  {'2Q+Vol':>8s}  {'2Q+Dep':>8s}  {'2Q only':>8s}  "
          f"{'Vol+Dep':>8s}  {'Vol only':>9s}  {'Dep only':>9s}")
    print("-" * 125)
    for model in sorted(all_data):
        for cfg in configs_seen:
            s = all_data[model].get(cfg)
            if s is None:
                continue
            n = s["valid_and_better"]
            t = total_circuits

            def fmt(k):
                v = s[k]
                return f"{v:3d} ({v/t*100:4.1f}%)"

            print(f"  {model:<25s}  {cfg:<16s}  "
                  f"{n:4d}/{t} ({n/t*100:4.1f}%)  "
                  f"{fmt('all3_improved'):>11s}  "
                  f"{fmt('twoq_vol_improved'):>8s}  "
                  f"{fmt('twoq_dep_improved'):>8s}  "
                  f"{fmt('twoq_only_improved'):>8s}  "
                  f"{fmt('vol_dep_improved'):>8s}  "
                  f"{fmt('vol_only_improved'):>9s}  "
                  f"{fmt('dep_only_improved'):>9s}")
    print("=" * 125)


# ── Stabilizer-size analysis ─────────────────────────────────────────
def print_stabilizer_size_analysis(all_rows: list[dict], configs_seen: list[str]):
    stab_vals = sorted([r["num_stabilizers"] for r in all_rows
                        if isinstance(r["num_stabilizers"], int)])
    if not stab_vals:
        print("\nNo stabilizer count data available.")
        return

    q1 = stab_vals[len(stab_vals) // 4]
    q2 = stab_vals[len(stab_vals) // 2]
    q3 = stab_vals[(3 * len(stab_vals)) // 4]
    buckets_order = ["Small", "Medium", "Large", "Extra-large"]

    def stab_bin(v):
        if v is None: return None
        if v <= q1:   return "Small"
        if v <= q2:   return "Medium"
        if v <= q3:   return "Large"
        return "Extra-large"

    print("\n" + "=" * 80)
    print("  STABILIZER-SIZE ANALYSIS  (does circuit complexity affect success?)")
    print(f"  Quartiles: Q1={q1}, Q2={q2}, Q3={q3}")
    print(f"  Small: ≤{q1}  |  Medium: {q1}<n≤{q2}  |  Large: {q2}<n≤{q3}  |  XL: >{q3}")
    print("=" * 80)

    by_model_bucket = defaultdict(lambda: defaultdict(list))
    for r in all_rows:
        b = stab_bin(r["num_stabilizers"])
        if b:
            by_model_bucket[r["model"]][b].append(r)

    print(f"\n  {'Model':<25s}  {'Bucket':<14s}  {'n':>5s}  {'Success':>8s}  {'Rate':>7s}  Trend")
    print("-" * 75)
    for model in sorted(by_model_bucket):
        prev = None
        for bucket in buckets_order:
            rows = by_model_bucket[model].get(bucket, [])
            n = len(rows)
            rate = sum(1 for r in rows if r["success"]) / n * 100 if n else 0
            trend = "" if prev is None else ("↑" if rate > prev + 1 else "↓" if rate < prev - 1 else "→")
            print(f"  {model:<25s}  {bucket:<14s}  {n:5d}  {sum(r['success'] for r in rows):8d}  {rate:6.1f}%  {trend}")
            prev = rate
        print()

    by_mcb = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for r in all_rows:
        b = stab_bin(r["num_stabilizers"])
        if b:
            by_mcb[r["model"]][r["cfg"]][b].append(r)

    print(f"  {'Model':<25s}  {'Config':<16s}  {'Bucket':<14s}  {'n':>5s}  {'Success':>8s}  {'Rate':>7s}  Trend")
    print("-" * 95)
    for model in sorted(by_mcb):
        for cfg in configs_seen:
            if cfg not in by_mcb[model]:
                continue
            prev = None
            for bucket in buckets_order:
                rows = by_mcb[model][cfg].get(bucket, [])
                n = len(rows)
                rate = sum(1 for r in rows if r["success"]) / n * 100 if n else 0
                trend = "" if prev is None else ("↑" if rate > prev + 1 else "↓" if rate < prev - 1 else "→")
                print(f"  {model:<25s}  {cfg:<16s}  {bucket:<14s}  {n:5d}  {sum(r['success'] for r in rows):8d}  {rate:6.1f}%  {trend}")
                prev = rate
        print()

    print("  SUMMARY — Small → Extra-large:")
    print(f"  {'Model':<25s}  {'Small':>8s}  {'Medium':>8s}  {'Large':>8s}  {'XLarge':>8s}  {'Δ':>8s}  Verdict")
    print("-" * 90)
    for model in sorted(by_model_bucket):
        rates = []
        for bucket in buckets_order:
            rows = by_model_bucket[model].get(bucket, [])
            n = len(rows)
            rates.append(sum(1 for r in rows if r["success"]) / n * 100 if n else float("nan"))
        delta = rates[-1] - rates[0] if not any(np.isnan(r) for r in rates) else float("nan")
        verdict = ("larger circuits HARDER" if delta < -5 else
                   "larger circuits easier" if delta > 5 else
                   "no clear size effect") if not np.isnan(delta) else "insufficient data"
        rate_strs = "  ".join(f"{r:7.1f}%" if not np.isnan(r) else "    N/A" for r in rates)
        print(f"  {model:<25s}  {rate_strs}  {f'{delta:+.1f}%' if not np.isnan(delta) else 'N/A':>8s}  {verdict}")
    print("=" * 80)


# ── Plotting ─────────────────────────────────────────────────────────
COLORS_POOL = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860", "#DA8BC3"]

def get_colors(configs_seen):
    return {cfg: COLORS_POOL[i % len(COLORS_POOL)] for i, cfg in enumerate(configs_seen)}

def plot_all(all_data: dict, configs_seen: list[str], output: str):
    colors = get_colors(configs_seen)
    models = list(all_data.keys())
    n_models, n_configs = len(models), len(configs_seen)
    bar_width = 0.8 / max(n_configs, 1)
    x = np.arange(n_models)

    fig, axes = plt.subplots(4, 2, figsize=(14, 17))
    fig.suptitle("Circuit Optimization — Model × Config Comparison",
                 fontsize=15, fontweight="bold")

    def grouped_bars(ax, metric_key, title, ylabel, fmt="{:.0f}%", is_pct=True):
        for i, cfg in enumerate(configs_seen):
            vals = [all_data[m][cfg][metric_key] if cfg in all_data[m] else 0 for m in models]
            offset = (i - (n_configs - 1) / 2) * bar_width
            bars = ax.bar(x + offset, vals, bar_width, label=cfg,
                          color=colors.get(cfg, f"C{i}"), edgecolor="white", linewidth=0.5)
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

    grouped_bars(axes[0, 0], "success_rate",    "Success Rate (Valid & Better)", "Rate (%)")
    grouped_bars(axes[0, 1], "valid_rate",       "Validity Rate", "Rate (%)")
    grouped_bars(axes[1, 0], "mean_cx_red",      "Mean CX Reduction (among successes)", "Reduction (%)")
    grouped_bars(axes[1, 1], "mean_dep_red",     "Mean Depth Reduction (among successes)", "Reduction (%)")
    grouped_bars(axes[2, 0], "mean_cx_red_all",  "Mean CX Reduction (over all circuits)", "Reduction (%)")
    grouped_bars(axes[2, 1], "mean_improvement_all", "Mean Improvement Magnitude (over all circuits)", "Reduction (%)")
    grouped_bars(axes[3, 0], "score",            "Composite Score", "Score (0–100)", fmt="{:.1f}", is_pct=False)
    axes[3, 0].set_ylim(0, 100)
    grouped_bars(axes[3, 1], "twoq_reduced_within_success_rate", "True 2Q Reduction (among successes)", "Rate (%)")

    plt.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    print(f"\n✓ Chart saved to {output}")

    # Capability + Quality score chart
    fig2, (ax_cap, ax_qual) = plt.subplots(1, 2, figsize=(14, 5))
    fig2.suptitle("Capability & Quality Scores", fontsize=13, fontweight="bold")

    for ax, key, title, ylabel in [
        (ax_cap, "capability_score", "Capability Score\nΣ I(valid & better) × stabilizers", "Score"),
        (ax_qual, "quality_score", "Quality Score\nΣ I(valid & better) × stabilizers × opt_proportion", "Score"),
    ]:
        for i, cfg in enumerate(configs_seen):
            vals = [all_data[m][cfg][key] if cfg in all_data[m] else 0 for m in models]
            offset = (i - (n_configs - 1) / 2) * bar_width
            bars = ax.bar(x + offset, vals, bar_width, label=cfg,
                          color=colors.get(cfg, f"C{i}"), edgecolor="white", linewidth=0.5)
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, h + 0.8,
                            f"{h:,.0f}", ha="center", va="bottom", fontsize=7)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=25, ha="right", fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)

    fig2.tight_layout()
    fig2.savefig(output.replace(".png", "_scores.png"), dpi=180, bbox_inches="tight")
    print(f"✓ Scores chart saved to {output.replace('.png', '_scores.png')}")


def plot_b2_difficulty_curve(all_rows: list[dict], output: str):
    """
    Cumulative difficulty curve for B2 — matches B1 style exactly.
    x = number of stabilizers, y = cumulative circuits successfully optimized
    with num_stabilizers <= x. One line per model at best config.
    """
    BEST_CONFIG = {
        "claude-opus-4.6":      "15 att / 900s",
        "gpt5.2":               "15 att / 900s",
        "gemini-3-pro-preview": "1 attempt",
    }
    MODEL_LABELS = {
        "claude-opus-4.6":      "Claude Opus 4.6",
        "gpt5.2":               "GPT-5.2",
        "gemini-3-pro-preview": "Gemini 3 Pro Preview",
    }
    AGENT_COLORS = {
        "Claude Opus 4.6":      "#E07B39",
        "GPT-5.2":              "#4C72B0",
        "Gemini 3 Pro Preview": "#55A868",
    }
    AGENT_MARKERS = {
        "Claude Opus 4.6":      "o",
        "GPT-5.2":              "s",
        "Gemini 3 Pro Preview": "D",
    }
    AGENT_LINESTYLES = {
        "Claude Opus 4.6":      "-",
        "GPT-5.2":              "--",
        "Gemini 3 Pro Preview": "-.",
    }
    AGENT_MARKER_OFFSET = {
        "Claude Opus 4.6":      0,
        "GPT-5.2":              2,
        "Gemini 3 Pro Preview": 4,
    }

    # Build per-(model, cfg) lookup: list of (num_stabilizers, success)
    from collections import defaultdict
    by_mc = defaultdict(list)
    for r in all_rows:
        if r["num_stabilizers"] is not None:
            by_mc[(r["model"], r["cfg"])].append(
                (r["num_stabilizers"], bool(r["success"]))
            )

    # All unique stabilizer counts across any best-config run
    all_stab_counts = sorted(set(
        stab
        for model, best_cfg in BEST_CONFIG.items()
        for stab, _ in by_mc[(model, best_cfg)]
    ))
    x_vals = np.array(all_stab_counts)

    fig, ax = plt.subplots(figsize=(9, 5.5))

    # Ceiling line: total circuits with num_stabilizers <= x
    ref_model = "claude-opus-4.6"
    ref_cfg = BEST_CONFIG[ref_model]
    all_stabs_ref = [stab for stab, _ in by_mc[(ref_model, ref_cfg)]]
    total_at_x = [sum(1 for s in all_stabs_ref if s <= x) for x in x_vals]
    ax.plot(x_vals, total_at_x, color="gray", linestyle="--", linewidth=1.5,
            label="Total benchmarks", alpha=0.7, zorder=1)
    ax.fill_between(x_vals, total_at_x, alpha=0.07, color="gray")

    for model, best_cfg in BEST_CONFIG.items():
        label = MODEL_LABELS[model]
        rows = by_mc[(model, best_cfg)]
        if not rows:
            continue

        solved_stabs = [stab for stab, success in rows if success]
        cumulative = [sum(1 for s in solved_stabs if s <= x) for x in x_vals]

        display_label = label
        if model == "gemini-3-pro-preview":
            display_label += "*"

        ax.plot(x_vals, cumulative,
                color=AGENT_COLORS[label],
                marker=AGENT_MARKERS[label],
                markersize=6,
                markevery=(AGENT_MARKER_OFFSET[label], 6),
                markeredgecolor="white",
                markeredgewidth=0.6,
                linestyle=AGENT_LINESTYLES[label],
                linewidth=2.2,
                label=display_label,
                zorder=2)

    ax.set_xlabel("Number of Stabilizers", fontsize=12)
    ax.set_ylabel("Circuits Successfully Optimized (cumulative)", fontsize=12)
    ax.set_title("B2 Difficulty Curve: Successful Optimizations vs. Stabilizer Count\n"
                 "(best config per agent)", fontsize=13, fontweight="bold")
    ax.legend(fontsize=9.5, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, max(x_vals) + 5)
    ax.set_ylim(0)
    ax.grid(axis="y", alpha=0.3)

    # Footnote for Gemini — placed below the axes
    fig.text(0.01, -0.03,
             "* Gemini evaluated at 1 attempt only; additional configurations not tested\n"
             "  (deleted its own output files during multi-attempt runs).",
             fontsize=8, color="gray", style="italic")

    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches="tight")
    print(f"✓ B2 difficulty curve saved to {output}")


def plot_stabilizer_size_paper(all_rows: list[dict], output: str):
    """Single-axes plot: one line per model (best config only) for paper figure."""
    # Best config per model
    BEST_CONFIG = {
        "claude-opus-4.6":        "15 att / 900s",
        "gpt5.2":                 "15 att / 900s",
        "gemini-3-pro-preview":   "1 attempt",
    }
    MODEL_LABELS = {
        "claude-opus-4.6":        "Claude Opus 4.6",
        "gpt5.2":                 "GPT-5.2",
        "gemini-3-pro-preview":   "Gemini Pro*",
    }
    COLORS = {
        "claude-opus-4.6":      "#4C72B0",
        "gpt5.2":               "#DD8452",
        "gemini-3-pro-preview": "#55A868",
    }
    MARKERS = {
        "claude-opus-4.6":      "o",
        "gpt5.2":               "s",
        "gemini-3-pro-preview": "^",
    }
    # Vertical offset (points) per model to stagger overlapping labels
    LABEL_OFFSET = {
        "claude-opus-4.6":      8,
        "gpt5.2":               -16,
        "gemini-3-pro-preview": 8,
    }

    stab_vals = sorted([r["num_stabilizers"] for r in all_rows
                        if isinstance(r["num_stabilizers"], int)])
    if not stab_vals:
        return

    q1 = stab_vals[len(stab_vals) // 4]
    q2 = stab_vals[len(stab_vals) // 2]
    q3 = stab_vals[(3 * len(stab_vals)) // 4]

    def stab_bin(v):
        if v is None: return None
        if v <= q1:   return "Small"
        if v <= q2:   return "Medium"
        if v <= q3:   return "Large"
        return "Extra-large"

    buckets = ["Small", "Medium", "Large", "Extra-large"]
    bucket_labels = [f"Small\n(≤{q1})", f"Medium\n(≤{q2})", f"Large\n(≤{q3})", f"XL\n(>{q3})"]

    by_mcb = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for r in all_rows:
        b = stab_bin(r["num_stabilizers"])
        if b:
            by_mcb[r["model"]][r["cfg"]][b].append(r)

    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(buckets))

    for model, best_cfg in BEST_CONFIG.items():
        if model not in by_mcb or best_cfg not in by_mcb[model]:
            continue
        rates = []
        for b in buckets:
            rows = by_mcb[model][best_cfg].get(b, [])
            n = len(rows)
            rates.append(sum(1 for r in rows if r["success"]) / n * 100 if n else np.nan)

        label = MODEL_LABELS[model]
        if model == "gemini-3-pro-preview":
            label += " (1 att, unreliable)"
            linestyle = "--"
        else:
            label += f" ({best_cfg})"
            linestyle = "-"

        ax.plot(x, rates, marker=MARKERS[model], color=COLORS[model],
                linestyle=linestyle, label=label, linewidth=2, markersize=8)
        # Only label first and last points to avoid clutter
        for xi_, yi_, b in zip(x, rates, buckets):
            if not np.isnan(yi_) and b in ("Small", "Extra-large"):
                # At XL, shift Gemini label down and GPT label up to avoid overlap
                if b == "Extra-large" and model == "gemini-3-pro-preview":
                    offset = -16
                elif b == "Extra-large" and model == "gpt5.2":
                    offset = 8
                else:
                    offset = LABEL_OFFSET[model]
                ax.annotate(f"{yi_:.0f}%", (xi_, yi_), textcoords="offset points",
                            xytext=(0, offset), ha="center", fontsize=9,
                            color=COLORS[model], fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(bucket_labels, fontsize=11)
    ax.set_xlabel("Circuit Complexity (# Stabilizers)", fontsize=12)
    ax.set_ylabel("Success Rate (%)", fontsize=12)
    ax.set_ylim(0, 120)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    print(f"✓ Paper difficulty chart saved to {output}")


def plot_stabilizer_size(all_rows: list[dict], configs_seen: list[str], output: str):
    stab_vals = sorted([r["num_stabilizers"] for r in all_rows
                        if isinstance(r["num_stabilizers"], int)])
    if not stab_vals:
        return

    q1 = stab_vals[len(stab_vals) // 4]
    q2 = stab_vals[len(stab_vals) // 2]
    q3 = stab_vals[(3 * len(stab_vals)) // 4]

    def stab_bin(v):
        if v is None: return None
        if v <= q1:   return "Small"
        if v <= q2:   return "Medium"
        if v <= q3:   return "Large"
        return "Extra-large"

    buckets = ["Small", "Medium", "Large", "Extra-large"]
    bucket_labels = [f"Small\n(≤{q1})", f"Medium\n(≤{q2})", f"Large\n(≤{q3})", f"XL\n(>{q3})"]

    by_mcb = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for r in all_rows:
        b = stab_bin(r["num_stabilizers"])
        if b:
            by_mcb[r["model"]][r["cfg"]][b].append(r)

    models = sorted(by_mcb.keys())
    colors = get_colors(configs_seen)
    markers = ["s", "^", "o", "D", "v", "p", "*"]

    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 5), sharey=True)
    if len(models) == 1:
        axes = [axes]
    fig.suptitle("Success Rate vs Circuit Complexity (# Stabilizers)\nper Model & Config",
                 fontsize=13, fontweight="bold")

    x = np.arange(len(buckets))
    for ax, model in zip(axes, models):
        for i, cfg in enumerate(configs_seen):
            if cfg not in by_mcb[model]:
                continue
            rates, ns = [], []
            for b in buckets:
                rows = by_mcb[model][cfg].get(b, [])
                n = len(rows)
                rates.append(sum(1 for r in rows if r["success"]) / n * 100 if n else np.nan)
                ns.append(n)
            valid_idx = [j for j, r in enumerate(rates) if not np.isnan(r)]
            xi = [x[j] for j in valid_idx]
            yi = [rates[j] for j in valid_idx]
            ax.plot(xi, yi, marker=markers[i % len(markers)], color=colors.get(cfg, f"C{i}"),
                    linestyle="-", label=cfg, linewidth=2)
            for xi_, yi_ in zip(xi, yi):
                ax.annotate(f"{yi_:.0f}%", (xi_, yi_), textcoords="offset points",
                            xytext=(0, 6), ha="center", fontsize=7, color=colors.get(cfg, f"C{i}"))
        ax.set_title(model, fontsize=11, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(bucket_labels, fontsize=8)
        ax.set_xlabel("Circuit Complexity (# Stabilizers)")
        ax.set_ylim(0, 115)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter())
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Success Rate (%)")
    plt.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    print(f"✓ Stabilizer-size chart saved to {output}")


def plot_combined_difficulty_curves(all_rows: list[dict], output: str):
    """
    3-panel figure: B1 | B2 | B3 difficulty curves, all in the same B1 style.
    B1 data: hardcoded from rq1 run.
    B2 data: computed from all_rows (best config per agent).
    B3 data: hardcoded from FT scoring run.
    """
    # ── Shared style constants ───────────────────────────────────────
    AGENT_COLORS = {
        "Claude Opus 4.6":      "#E07B39",
        "GPT-5.2":              "#4C72B0",
        "Gemini 3 Pro Preview": "#55A868",
        "GPT-4.1":              "#9467BD",
    }
    AGENT_MARKERS = {
        "Claude Opus 4.6":      "o",
        "GPT-5.2":              "s",
        "Gemini 3 Pro Preview": "D",
        "GPT-4.1":              "^",
    }
    AGENT_LINESTYLES = {
        "Claude Opus 4.6":      "-",
        "GPT-5.2":              "--",
        "Gemini 3 Pro Preview": "-.",
        "GPT-4.1":              ":",
    }
    AGENT_MARKER_OFFSET = {
        "Claude Opus 4.6":      0,
        "GPT-5.2":              2,
        "Gemini 3 Pro Preview": 4,
        "GPT-4.1":              1,
    }
    AGENT_ORDER = ["GPT-4.1", "Claude Opus 4.6", "GPT-5.2", "Gemini 3 Pro Preview"]

    # ── Shared ceiling (stabilizer-weighted, max = 16,340) ──────────
    TOTAL_SCAP = [
        (2,10),(4,14),(6,32),(8,56),(10,66),(14,80),(16,96),(18,150),(20,170),
        (22,192),(24,240),(26,448),(30,478),(34,852),(36,888),(38,1116),(44,1292),
        (48,1772),(50,2122),(58,2296),(62,3040),(66,3304),(68,3372),(72,3444),
        (74,3740),(80,4060),(82,4306),(84,4474),(86,4646),(90,4916),(94,5104),
        (98,5790),(104,6414),(106,6626),(110,6846),(114,7188),(118,7896),(122,8140),
        (124,8388),(128,8644),(130,8774),(132,9566),(134,10370),(146,11100),
        (152,11708),(154,12016),(160,12976),(164,13140),(170,13820),(174,14864),
        (178,15220),(182,15584),(184,15952),(194,16340),
    ]
    SCAP_MAX = 16340

    # ── B1 S_cap data ────────────────────────────────────────────────
    B1_AGENT = {
        "Claude Opus 4.6": [
            (2,10),(4,14),(6,26),(8,50),(10,60),(14,74),(16,90),(18,144),(20,164),
            (22,186),(24,234),(26,442),(30,472),(34,846),(36,882),(38,1110),(44,1286),
            (48,1766),(50,2116),(58,2290),(62,3034),(66,3298),(68,3366),(72,3438),
            (74,3734),(80,4054),(82,4300),(84,4468),(86,4640),(90,4910),(94,5098),
            (98,5686),(104,6310),(106,6416),(110,6636),(114,6978),(118,7686),(122,7930),
            (124,8178),(128,8434),(130,8564),(132,9356),(134,10160),(146,10744),
            (152,11048),(154,11048),(160,11528),(164,11528),(170,11528),(174,11528),
            (178,11528),(182,11528),(184,11528),(194,11528),
        ],
        "GPT-5.2": [
            (2,10),(4,14),(6,32),(8,56),(10,66),(14,80),(16,96),(18,150),(20,170),
            (22,192),(24,240),(26,448),(30,478),(34,852),(36,888),(38,1116),(44,1292),
            (48,1772),(50,2122),(58,2296),(62,3040),(66,3304),(68,3372),(72,3444),
            (74,3740),(80,4060),(82,4306),(84,4474),(86,4646),(90,4916),(94,5104),
            (98,5594),(104,6218),(106,6324),(110,6544),(114,6886),(118,7594),(122,7716),
            (124,7840),(128,8096),(130,8226),(132,8886),(134,9690),(146,9836),
            (152,10292),(154,10292),(160,10932),(164,10932),(170,10932),(174,11106),
            (178,11106),(182,11106),(184,11106),(194,11106),
        ],
        "Gemini 3 Pro Preview": [
            (2,10),(4,14),(6,32),(8,56),(10,66),(14,80),(16,96),(18,150),(20,170),
            (22,192),(24,240),(26,448),(30,478),(34,852),(36,888),(38,1116),(44,1292),
            (48,1772),(50,2122),(58,2296),(62,3040),(66,3304),(68,3372),(72,3444),
            (74,3740),(80,3980),(82,4226),(84,4310),(86,4482),(90,4752),(94,4940),
            (98,5626),(104,6042),(106,6254),(110,6474),(114,6702),(118,7292),(122,7536),
            (124,7536),(128,7664),(130,7794),(132,8190),(134,8592),(146,9030),
            (152,9638),(154,9792),(160,10112),(164,10112),(170,10452),(174,10800),
            (178,11156),(182,11156),(184,11340),(194,11340),
        ],
        "GPT-4.1": [
            (2,4),(4,4),(6,4),(8,4),(10,4),(14,4),(16,4),(18,4),(20,4),(22,4),
            (24,4),(26,4),(30,4),(34,4),(36,4),(38,4),(44,4),(48,4),(50,4),
            (58,4),(62,4),(66,4),(68,4),(72,4),(74,4),(80,4),(82,4),(84,4),
            (86,4),(90,4),(94,4),(98,4),(104,4),(106,4),(110,4),(114,4),
            (118,4),(122,4),(124,4),(128,4),(130,4),(132,4),(134,4),(146,4),
            (152,4),(154,4),(160,4),(164,4),(170,4),(174,4),(178,4),(182,4),
            (184,4),(194,4),
        ],
    }

    # ── B2 S_cap computed from all_rows ──────────────────────────────
    B2_BEST_CONFIG = {
        "claude-opus-4.6":      ("Claude Opus 4.6",      "15 att / 900s"),
        "gpt5.2":               ("GPT-5.2",              "15 att / 900s"),
        "gemini-3-pro-preview": ("Gemini 3 Pro Preview", "1 attempt"),
    }
    from collections import defaultdict
    by_mc = defaultdict(list)
    for r in all_rows:
        if r["num_stabilizers"] is not None:
            by_mc[(r["model"], r["cfg"])].append(
                (r["num_stabilizers"], bool(r["success"]))
            )
    b2_all_stabs = set()
    b2_raw = {}
    for model_key, (label, cfg) in B2_BEST_CONFIG.items():
        rows = by_mc[(model_key, cfg)]
        b2_raw[label] = rows
        b2_all_stabs.update(s for s, _ in rows)
    b2_x = np.array(sorted(b2_all_stabs))
    # Cumulative S_cap: sum num_stabilizers for successful circuits with stab <= x
    b2_agent = {}
    for label, rows in b2_raw.items():
        solved_stabs = [s for s, ok in rows if ok]
        b2_agent[label] = [(int(x), sum(s for s in solved_stabs if s <= x)) for x in b2_x]
    total_scap_dict = dict(TOTAL_SCAP)
    b2_total = [total_scap_dict.get(int(x), 0) for x in b2_x]

    # ── B3 S_cap data ────────────────────────────────────────────────
    B3_AGENT = {
        "Claude Opus 4.6": [
            (2,10),(4,14),(6,32),(8,56),(10,66),(14,80),(16,96),(18,132),(20,152),
            (22,152),(24,176),(26,306),(30,306),(34,544),(36,580),(38,618),(44,618),
            (48,762),(50,912),(58,912),(62,1284),(66,1350),(68,1350),(72,1350),
            (74,1424),(80,1584),(82,1748),(84,1748),(86,1748),(90,1838),(94,1838),
            (98,1838),(104,2046),(106,2152),(110,2152),(114,2266),(118,2384),(122,2384),
            (124,2384),(128,2384),(130,2384),(132,2384),(134,2652),(146,2652),
            (152,2652),(154,2652),(160,2652),(164,2652),(170,2652),(174,2652),
            (178,2830),(182,2830),(184,2830),(194,2830),
        ],
        "GPT-5.2": [
            (2,10),(4,14),(6,26),(8,42),(10,42),(14,56),(16,56),(18,92),(20,112),
            (22,112),(24,112),(26,216),(30,216),(34,454),(36,454),(38,492),(44,624),
            (48,768),(50,868),(58,868),(62,1178),(66,1310),(68,1310),(72,1310),
            (74,1384),(80,1544),(82,1708),(84,1708),(86,1794),(90,1794),(94,1794),
            (98,1794),(104,2106),(106,2106),(110,2106),(114,2220),(118,2220),(122,2220),
            (124,2220),(128,2220),(130,2220),(132,2220),(134,2220),(146,2220),
            (152,2220),(154,2220),(160,2220),(164,2220),(170,2220),(174,2220),
            (178,2220),(182,2220),(184,2220),(194,2220),
        ],
        "Gemini 3 Pro Preview": [
            (2,10),(4,14),(6,26),(8,50),(10,60),(14,74),(16,90),(18,126),(20,126),
            (22,126),(24,126),(26,204),(30,204),(34,238),(36,238),(38,276),(44,276),
            (48,276),(50,276),(58,276),(62,276),(66,276),(68,276),(72,276),(74,276),
            (80,276),(82,276),(84,276),(86,276),(90,276),(94,276),(98,276),(104,276),
            (106,276),(110,276),(114,276),(118,276),(122,276),(124,276),(128,276),
            (130,276),(132,276),(134,276),(146,276),(152,276),(154,276),(160,276),
            (164,276),(170,276),(174,276),(178,276),(182,276),(184,276),(194,276),
        ],
    }
    b3_x = np.array(sorted(set(x for pts in B3_AGENT.values() for x, _ in pts)))
    b3_total = [total_scap_dict.get(int(x), 0) for x in b3_x]

    # ── Build figure ─────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    scap_x = np.array([x for x, _ in TOTAL_SCAP])
    scap_y = [y for _, y in TOTAL_SCAP]
    panels = [
        ("B1: Stabilizer Synthesis",  r"Cumulative $S_{\mathrm{cap}}$", B1_AGENT, scap_x, scap_y),
        ("B2: Circuit Optimization",  r"Cumulative $S_{\mathrm{cap}}$", b2_agent, b2_x,   b2_total),
        ("B3: Fault-Tolerance",       r"Cumulative $S_{\mathrm{cap}}$", B3_AGENT, b3_x,   b3_total),
    ]

    handles, labels_legend = None, None
    for ax, (title, ylabel, agent_data, x_vals, total_ceil) in zip(axes, panels):
        # Ceiling line
        ax.plot(x_vals, total_ceil, color="gray", linestyle="--", linewidth=1.5,
                label="Total benchmarks", alpha=0.7, zorder=1)
        ax.fill_between(x_vals, total_ceil, alpha=0.07, color="gray")

        for agent_label in AGENT_ORDER:
            pts = agent_data.get(agent_label)
            if pts is None:
                continue
            xs = np.array([x for x, _ in pts])
            ys = np.array([y for _, y in pts])

            ax.plot(xs, ys,
                    color=AGENT_COLORS[agent_label],
                    marker=AGENT_MARKERS[agent_label],
                    markersize=6,
                    markevery=(AGENT_MARKER_OFFSET[agent_label], 6),
                    markeredgecolor="white",
                    markeredgewidth=0.6,
                    linestyle=AGENT_LINESTYLES[agent_label],
                    linewidth=2.2,
                    label=agent_label,
                    zorder=2)

        ax.set_xlabel("Number of Stabilizers", fontsize=11)
        if ax is axes[0]:
            ax.set_ylabel(ylabel, fontsize=10)
        else:
            ax.tick_params(labelleft=False)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlim(0, max(x_vals) + 5)
        ax.set_ylim(0, SCAP_MAX * 1.05)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
        ax.grid(axis="y", alpha=0.3)

        if handles is None:
            handles, labels_legend = ax.get_legend_handles_labels()

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.28)

    # Single shared legend below all panels — placed after tight_layout so spacing is stable
    fig.legend(handles, labels_legend, loc="lower center", ncol=4,
               fontsize=10, frameon=False,
               bbox_to_anchor=(0.5, 0.08))

    fig.savefig(output, dpi=200, bbox_inches="tight")
    print(f"✓ Combined difficulty curves saved to {output}")


# ── Main ─────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_models.py <data_directory>")
        sys.exit(1)

    data_dir = sys.argv[1]
    print(f"Scanning {data_dir} ...\n")
    all_data, all_rows, configs_seen = discover(data_dir)

    if not all_data:
        print("No model data found. Check ANALYSIS_CONFIG at the top of the script.")
        sys.exit(1)

    print_score_summary(all_data, configs_seen)
    print_metric_breakdown(all_data, configs_seen)
    print_stabilizer_size_analysis(all_rows, configs_seen)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_comparison.png")
    plot_all(all_data, configs_seen, out)
    plot_stabilizer_size(all_rows, configs_seen, out.replace("model_comparison", "stabilizer_size_analysis"))
    plot_stabilizer_size_paper(all_rows, out.replace("model_comparison", "b2_difficulty"))
    plot_b2_difficulty_curve(all_rows, out.replace("model_comparison", "b2_difficulty_curve"))
    plot_combined_difficulty_curves(all_rows, out.replace("model_comparison", "combined_difficulty_curves"))


if __name__ == "__main__":
    main()