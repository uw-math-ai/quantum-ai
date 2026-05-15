"""
Combined Difficulty Curves — B1 | B2 | B3
------------------------------------------
3-panel figure of cumulative S_cap vs. number of stabilizers,
one panel per benchmark.

B1 and B3 use hardcoded S_cap data from prior runs.
B2 is recomputed from raw result files via analysis/B2/analyze_models.discover().

Usage:
    python analysis/plot_combined_difficulty_curves.py <B2_data_directory>

Output:
    analysis/combined_difficulty_curves.png
"""

import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Reuse B2's discovery to compute all_rows for the B2 panel.
sys.path.insert(0, str(Path(__file__).resolve().parent / "B2"))
from analyze_models import discover  # noqa: E402


# ── Shared style constants ───────────────────────────────────────────
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

# Shared ceiling (stabilizer-weighted, max = 16,340)
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

# ── B1 S_cap data ────────────────────────────────────────────────────
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

# ── B3 S_cap data ────────────────────────────────────────────────────
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


def compute_b2_panel(all_rows: list[dict]):
    """Build B2 cumulative S_cap series from analyze_models.discover() rows."""
    B2_BEST_CONFIG = {
        "claude-opus-4.6":      ("Claude Opus 4.6",      "15 att / 900s"),
        "gpt5.2":               ("GPT-5.2",              "15 att / 900s"),
        "gemini-3-pro-preview": ("Gemini 3 Pro Preview", "1 attempt"),
    }
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
    b2_agent = {}
    for label, rows in b2_raw.items():
        solved_stabs = [s for s, ok in rows if ok]
        b2_agent[label] = [(int(x), sum(s for s in solved_stabs if s <= x)) for x in b2_x]
    total_scap_dict = dict(TOTAL_SCAP)
    b2_total = [total_scap_dict.get(int(x), 0) for x in b2_x]
    return b2_agent, b2_x, b2_total


def plot_combined_difficulty_curves(all_rows: list[dict], output: str):
    b2_agent, b2_x, b2_total = compute_b2_panel(all_rows)

    total_scap_dict = dict(TOTAL_SCAP)
    b3_x = np.array(sorted(set(x for pts in B3_AGENT.values() for x, _ in pts)))
    b3_total = [total_scap_dict.get(int(x), 0) for x in b3_x]

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

    fig.legend(handles, labels_legend, loc="lower center", ncol=4,
               fontsize=10, frameon=False,
               bbox_to_anchor=(0.5, 0.08))

    fig.savefig(output, dpi=200, bbox_inches="tight")
    print(f"✓ Combined difficulty curves saved to {output}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_combined_difficulty_curves.py <B2_data_directory>")
        sys.exit(1)

    data_dir = sys.argv[1]
    print(f"Scanning B2 data at {data_dir} ...\n")
    _, all_rows, _ = discover(data_dir)

    output = str(Path(__file__).resolve().parent / "combined_difficulty_curves.png")
    plot_combined_difficulty_curves(all_rows, output)


if __name__ == "__main__":
    main()
