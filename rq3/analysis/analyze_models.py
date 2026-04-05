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

Usage:
    python analyze_models.py <data_directory>
"""

import json, sys, os, glob
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


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
    return f"{attempts} att / {timeout}s"

CONFIG_ORDER = ["1 attempt", "15 att / 300s", "15 att / 900s"]
MODELS_TO_ANALYZE = {"claude-opus-4.6", "gpt5.2", "gemini-3-pro-preview"}


# ── Stat extraction ──────────────────────────────────────────────────
def improvement_magnitude(bm: dict, om: dict) -> float:
    """2Q-gate reduction % if 2Q improved, else volume, else depth (mirrors lexicographic is_better)."""
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
    # Metric improvement breakdown (among valid+better circuits)
    all3_improved = 0        # 2Q↓ + vol↓ + dep↓
    twoq_vol_improved = 0    # 2Q↓ + vol↓  (dep same/higher)
    twoq_dep_improved = 0    # 2Q↓ + dep↓  (vol same/higher)
    twoq_only_improved = 0   # 2Q↓ only
    vol_dep_improved = 0     # vol↓ + dep↓  (2Q same)
    vol_only_improved = 0    # vol↓ only    (2Q same)
    dep_only_improved = 0    # dep↓ only    (2Q same, vol same)

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

            # Use two_qubit_gates if available, fall back to cx_count
            twoq_b = bm.get("two_qubit_gates", bm.get("cx_count", 0))
            twoq_o = om.get("two_qubit_gates", om.get("cx_count", twoq_b))
            vol_b  = bm.get("volume", 0)
            vol_o  = om.get("volume", vol_b)
            dep_b  = bm.get("depth", 0)
            dep_o  = om.get("depth", dep_b)

            twoq_imp = twoq_o < twoq_b
            vol_imp  = vol_o  < vol_b
            dep_imp  = dep_o  < dep_b

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

    weighted_score = max_weighted_score = 0
    if stab_counts:
        for r in results:
            n_stab = stab_counts.get(r.get("code_name", ""), 0)
            max_weighted_score += n_stab
            if r.get("valid") and r.get("better"):
                weighted_score += n_stab

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
        "weighted_score": weighted_score,
        "max_weighted_score": max_weighted_score,
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


# ── Discovery ────────────────────────────────────────────────────────
def discover(data_dir: str) -> tuple[dict, list[dict]]:
    """Returns ({model_name: {config_label: stats_dict}}, [raw_rows])"""
    stab_counts = load_stabilizer_counts(data_dir)
    if stab_counts:
        print(f"  Loaded stabilizer counts for {len(stab_counts)} circuits.\n")
    else:
        print("  Warning: could not load circuit_dataset.jsonl — stabilizer analysis unavailable.\n")

    all_data = {}
    all_rows = []

    for model_dir in sorted(glob.glob(os.path.join(data_dir, "*"))):
        if not os.path.isdir(model_dir):
            continue
        model_name = os.path.basename(model_dir)
        if model_name not in MODELS_TO_ANALYZE:
            continue

        json_files = sorted(glob.glob(os.path.join(model_dir, "*.json")))
        if not json_files:
            continue

        configs = {}
        for jf in json_files:
            with open(jf) as f:
                data = json.load(f)
            cfg = classify_config(data.get("metadata", {}))
            stats = extract_stats(data, stab_counts)
            configs[cfg] = stats
            print(f"  {model_name:25s}  {cfg:16s}  n={stats['total']:3d}  "
                  f"success={stats['success_rate']:5.1f}%  score={stats['score']:5.1f}")

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

        all_data[model_name] = configs
    return all_data, all_rows


# ── Score summary ────────────────────────────────────────────────────
def print_score_summary(all_data: dict):
    print("\n" + "=" * 100)
    print("  RQ3 BENCHMARK SCORES")
    print("  Score = 0.50 × SuccessRate + 0.50 × MeanImprovementMagnitude(all)")
    print("  Weighted Score = Σ I(valid & better) × num_stabilizers / Σ num_stabilizers × 100  (raw counts in parens)")
    print("=" * 100)
    print(f"  {'Model':<25s}  {'Config':<16s}  {'Success':>8s}  {'CX↓(succ)':>10s}  "
          f"{'CX↓(all)':>9s}  {'Imp(all)':>9s}  {'SCORE':>6s}  {'Weighted Score':>20s}")
    print("-" * 100)
    for model in sorted(all_data.keys()):
        for cfg in CONFIG_ORDER:
            s = all_data[model].get(cfg)
            if s is None:
                continue
            ws, ms = s["weighted_score"], s["max_weighted_score"]
            ws_str = f"{ws/ms*100:5.1f}  ({ws:,} / {ms:,})" if ms else "N/A"
            print(f"  {model:<25s}  {cfg:<16s}  {s['success_rate']:7.1f}%  "
                  f"{s['mean_cx_red']:9.1f}%  "
                  f"{s['mean_cx_red_all']:8.1f}%  "
                  f"{s['mean_improvement_all']:8.1f}%  "
                  f"{s['score']:6.1f}  "
                  f"{ws_str:>20s}")
    print("=" * 100)


# ── Metric improvement breakdown ────────────────────────────────────
def print_metric_breakdown(all_data: dict):
    """For each model×config, break down what metric combinations were improved."""
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
        for cfg in CONFIG_ORDER:
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
def print_stabilizer_size_analysis(all_rows: list[dict]):
    """Success rate by stabilizer-count bucket, per model and per model×config."""
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

    # ── Per model (pooled across configs) ──
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

    # ── Per model × config ──
    print(f"  {'Model':<25s}  {'Config':<16s}  {'Bucket':<14s}  {'n':>5s}  {'Success':>8s}  {'Rate':>7s}  Trend")
    print("-" * 95)
    by_mcb = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for r in all_rows:
        b = stab_bin(r["num_stabilizers"])
        if b:
            by_mcb[r["model"]][r["cfg"]][b].append(r)

    for model in sorted(by_mcb):
        for cfg in CONFIG_ORDER:
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

    # ── Summary ──
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
COLORS = {
    "1 attempt":      "#4C72B0",
    "15 att / 300s":  "#DD8452",
    "15 att / 900s":  "#55A868",
}

def plot_all(all_data: dict, output: str):
    models = list(all_data.keys())
    seen_configs = sorted(
        {cfg for m in all_data.values() for cfg in m},
        key=lambda c: CONFIG_ORDER.index(c) if c in CONFIG_ORDER else 99
    )
    n_models, n_configs = len(models), len(seen_configs)
    bar_width = 0.8 / max(n_configs, 1)
    x = np.arange(n_models)

    fig, axes = plt.subplots(4, 2, figsize=(14, 17))
    fig.suptitle("Circuit Optimization — Model × Config Comparison",
                 fontsize=15, fontweight="bold")

    def grouped_bars(ax, metric_key, title, ylabel, fmt="{:.0f}%", is_pct=True):
        for i, cfg in enumerate(seen_configs):
            vals = [all_data[m][cfg][metric_key] if cfg in all_data[m] else 0 for m in models]
            offset = (i - (n_configs - 1) / 2) * bar_width
            bars = ax.bar(x + offset, vals, bar_width, label=cfg,
                          color=COLORS.get(cfg, f"C{i}"), edgecolor="white", linewidth=0.5)
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
    grouped_bars(axes[3, 0], "score",            "RQ3 Benchmark Score", "Score (0–100)", fmt="{:.1f}", is_pct=False)
    axes[3, 0].set_ylim(0, 100)
    axes[3, 0].axhline(y=50, color="gray", linestyle="--", alpha=0.3)
    grouped_bars(axes[3, 1], "twoq_reduced_within_success_rate", "True 2Q Reduction (among successes)", "Rate (%)")

    plt.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    print(f"\n✓ Chart saved to {output}")

    # Weighted score chart
    fig2, ax_ws = plt.subplots(figsize=(8, 4))
    fig2.suptitle("Stabilizer-Weighted Score  (normalized 0–100)", fontsize=12, fontweight="bold")
    for i, cfg in enumerate(seen_configs):
        vals = []
        for m in models:
            s = all_data[m].get(cfg)
            ws, ms = (s["weighted_score"], s["max_weighted_score"]) if s else (0, 0)
            vals.append(ws / ms * 100 if ms else 0)
        offset = (i - (n_configs - 1) / 2) * bar_width
        bars = ax_ws.bar(x + offset, vals, bar_width, label=cfg,
                         color=COLORS.get(cfg, f"C{i}"), edgecolor="white", linewidth=0.5)
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax_ws.text(bar.get_x() + bar.get_width() / 2, h + 0.8,
                           f"{h:.1f}", ha="center", va="bottom", fontsize=7)
    ax_ws.set_ylim(0, 110)
    ax_ws.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax_ws.set_ylabel("Weighted Score (0–100)")
    ax_ws.set_xticks(x)
    ax_ws.set_xticklabels(models, rotation=25, ha="right", fontsize=9)
    ax_ws.legend(fontsize=8)
    ax_ws.grid(axis="y", alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(output.replace(".png", "_weighted.png"), dpi=180, bbox_inches="tight")
    print(f"✓ Weighted score chart saved to {output.replace('.png', '_weighted.png')}")


def plot_stabilizer_size(all_rows: list[dict], output: str):
    """One subplot per model, one line per config — success rate vs stabilizer-size bucket."""
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
    CFG_STYLES = {
        "1 attempt":     {"color": "#4C72B0", "ls": "--",  "marker": "s"},
        "15 att / 300s": {"color": "#DD8452", "ls": "-.",  "marker": "^"},
        "15 att / 900s": {"color": "#55A868", "ls": "-",   "marker": "o"},
    }

    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 5), sharey=True)
    if len(models) == 1:
        axes = [axes]
    fig.suptitle("Success Rate vs Circuit Complexity (# Stabilizers)\nper Model & Config",
                 fontsize=13, fontweight="bold")

    x = np.arange(len(buckets))
    for ax, model in zip(axes, models):
        for cfg in CONFIG_ORDER:
            if cfg not in by_mcb[model]:
                continue
            style = CFG_STYLES.get(cfg, {"color": "gray", "ls": "-", "marker": "o"})
            rates, ns = [], []
            for b in buckets:
                rows = by_mcb[model][cfg].get(b, [])
                n = len(rows)
                rates.append(sum(1 for r in rows if r["success"]) / n * 100 if n else np.nan)
                ns.append(n)
            valid_idx = [i for i, r in enumerate(rates) if not np.isnan(r)]
            xi, yi, ni = [x[i] for i in valid_idx], [rates[i] for i in valid_idx], [ns[i] for i in valid_idx]
            ax.plot(xi, yi, marker=style["marker"], color=style["color"],
                    linestyle=style["ls"], label=cfg, linewidth=2)
            for xi_, yi_, n_ in zip(xi, yi, ni):
                ax.annotate(f"{yi_:.0f}%", (xi_, yi_), textcoords="offset points",
                            xytext=(0, 6), ha="center", fontsize=7, color=style["color"])
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
    print_metric_breakdown(all_data)
    print_stabilizer_size_analysis(all_rows)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_comparison.png")
    plot_all(all_data, out)
    plot_stabilizer_size(all_rows, out.replace("model_comparison", "stabilizer_size_analysis"))


if __name__ == "__main__":
    main()
