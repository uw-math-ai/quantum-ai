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

import json, sys, os
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

    cx_reds = []
    improvement_mags_all = []

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
            improvement_mags_all.append(0.0)

    success_rate = valid_and_better / total * 100 if total else 0
    mean_improvement_all = np.mean(improvement_mags_all) if improvement_mags_all else 0

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
        "success_rate": success_rate,
        "mean_cx_red": np.mean(cx_reds) if cx_reds else 0,
        "mean_improvement_all": mean_improvement_all,
        "capability_score": capability_score,
        "max_capability_score": max_capability_score,
        "quality_score": quality_score,
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

def plot_scores(all_data: dict, configs_seen: list[str], output: str):
    """Capability + Quality scores side-by-side."""
    colors = get_colors(configs_seen)
    models = list(all_data.keys())
    n_models, n_configs = len(models), len(configs_seen)
    bar_width = 0.8 / max(n_configs, 1)
    x = np.arange(n_models)

    fig, (ax_cap, ax_qual) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Capability & Quality Scores", fontsize=13, fontweight="bold")

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

    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    print(f"✓ Scores chart saved to {output}")


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

    diagrams_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)
    plot_b2_difficulty_curve(all_rows, os.path.join(diagrams_dir, "b2_difficulty_curve.png"))
    plot_scores(all_data, configs_seen, os.path.join(diagrams_dir, "model_comparison_scores.png"))
    plot_stabilizer_size(all_rows, configs_seen, os.path.join(diagrams_dir, "stabilizer_size_analysis.png"))


if __name__ == "__main__":
    main()