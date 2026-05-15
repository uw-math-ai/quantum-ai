#!/usr/bin/env python3
"""
Plot difficulty curve: for each agent, the number of codes perfectly solved
(under any config) as a function of the number of stabilizers.
"""

import json
import os
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# ==============================================================================
# Configuration
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parents[2] / "B1"
DATA_DIR = BASE_DIR / "data"
BENCHMARKS_PATH = BASE_DIR.parent / "data" / "benchmarks.json"

AGENTS = {
    "claude-opus-4.6": "Claude Opus 4.6",
    "gemini-3-pro-preview": "Gemini 3 Pro Preview",
    "gpt5.2": "GPT-5.2",
}

AGENT_COLORS = {
    "Claude Opus 4.6": "#E07B39",
    "GPT-5.2": "#4C72B0",
    "Gemini 3 Pro Preview": "#55A868",
}

AGENT_MARKERS = {
    "Claude Opus 4.6": "o",
    "GPT-5.2": "s",
    "Gemini 3 Pro Preview": "D",
}

AGENT_LINESTYLES = {
    "Claude Opus 4.6": "-",
    "GPT-5.2": "--",
    "Gemini 3 Pro Preview": "-.",
}

# Stagger markers so they don't land on the same x positions
AGENT_MARKER_OFFSET = {
    "Claude Opus 4.6": 0,
    "GPT-5.2": 2,
    "Gemini 3 Pro Preview": 4,
}

# ==============================================================================
# Load benchmarks to get stabilizer counts
# ==============================================================================
with open(BENCHMARKS_PATH) as f:
    benchmarks = json.load(f)

code_info = {}
for b in benchmarks:
    code_info[b["name"]] = {
        "num_generators": len(b["generators"]),
        "physical_qubits": b["physical_qubits"],
    }

# ==============================================================================
# Load results: for each agent, find codes perfectly solved under ANY config
# ==============================================================================
# agent_label -> set of perfectly-solved code names
agent_solved = defaultdict(set)

for agent_dir_name, agent_label in AGENTS.items():
    agent_dir = DATA_DIR / agent_dir_name
    for json_file in sorted(agent_dir.glob("2602*.json")):
        with open(json_file) as f:
            data = json.load(f)
        for r in data["results"]:
            if r["success_rate"] == 1.0:
                agent_solved[agent_label].add(r["code_name"])

# ==============================================================================
# Build cumulative curves: at each stabilizer count x, how many codes with
# num_generators <= x did the agent perfectly solve?
# ==============================================================================

# Get all stabilizer counts across the benchmark suite
all_gen_counts = sorted(set(code_info[name]["num_generators"] for name in code_info))

# For a smooth curve, evaluate at every unique stabilizer count
x_vals = np.array(all_gen_counts)

fig, ax = plt.subplots(figsize=(9, 5.5))

# Also plot the total benchmark count as a reference line
total_at_x = []
for x in x_vals:
    total_at_x.append(sum(1 for name in code_info if code_info[name]["num_generators"] <= x))
ax.plot(x_vals, total_at_x, color="gray", linestyle="--", linewidth=1.5,
        label="Total benchmarks", alpha=0.7, zorder=1)
ax.fill_between(x_vals, total_at_x, alpha=0.07, color="gray")

for agent_label in ["Claude Opus 4.6", "GPT-5.2", "Gemini 3 Pro Preview"]:
    solved_names = agent_solved[agent_label]
    cumulative = []
    for x in x_vals:
        count = sum(
            1 for name in solved_names
            if code_info[name]["num_generators"] <= x
        )
        cumulative.append(count)
    offset = AGENT_MARKER_OFFSET[agent_label]
    n_pts = len(x_vals)
    ax.plot(x_vals, cumulative,
            color=AGENT_COLORS[agent_label],
            marker=AGENT_MARKERS[agent_label],
            markersize=6,
            markevery=(offset, 6),
            markeredgecolor="white",
            markeredgewidth=0.6,
            linestyle=AGENT_LINESTYLES[agent_label],
            linewidth=2.2,
            label=agent_label,
            zorder=2)

ax.set_xlabel("Number of Stabilizers", fontsize=12)
ax.set_ylabel("Codes Perfectly Solved (cumulative)", fontsize=12)
ax.set_title("B1 Difficulty Curve: Perfect Solves vs. Stabilizer Count\n(best config per agent per code)",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=9.5, loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlim(0, max(x_vals) + 5)
ax.set_ylim(0, 200)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
OUT_DIR = Path(__file__).resolve().parent / "diagrams"
OUT_DIR.mkdir(exist_ok=True)
plt.savefig(OUT_DIR / "difficulty_curve.png", dpi=200, bbox_inches="tight")
plt.savefig(OUT_DIR / "difficulty_curve.pdf", bbox_inches="tight")
print(f"Saved {OUT_DIR}/difficulty_curve.png and .pdf")
plt.show()
