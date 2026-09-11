"""Plot cumulative capability and quality curves for all benchmark results.

Completed runs are discovered under B1/data, B2/data, and B3/data. For every
model in each benchmark, the completed run with the highest S_cap is selected.
Set an entry in RUN_OVERRIDES to choose a specific run instead.

Usage:
    python analysis/plot_combined_difficulty_curves.py

Outputs:
    analysis/combined_difficulty_curves.png
    analysis/combined_quality_difficulty_curves.png
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "B2"))
from analyze_models import optimization_proportion  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DATA_DIRS = {name: ROOT / name / "data" for name in ("B1", "B2", "B3")}
OUTPUT_DIR = Path(__file__).resolve().parent

# Use paths relative to the matching B<n>/data directory. Empty by default:
# the highest-S_cap completed run is selected automatically for every model.
RUN_OVERRIDES: dict[str, dict[str, str]] = {"B1": {}, "B2": {}, "B3": {}}

TOTAL_SCAP = [
    (2, 10), (4, 14), (6, 32), (8, 56), (10, 66), (14, 80), (16, 96),
    (18, 150), (20, 170), (22, 192), (24, 240), (26, 448), (30, 478),
    (34, 852), (36, 888), (38, 1116), (44, 1292), (48, 1772), (50, 2122),
    (58, 2296), (62, 3040), (66, 3304), (68, 3372), (72, 3444), (74, 3740),
    (80, 4060), (82, 4306), (84, 4474), (86, 4646), (90, 4916), (94, 5104),
    (98, 5790), (104, 6414), (106, 6626), (110, 6846), (114, 7188),
    (118, 7896), (122, 8140), (124, 8388), (128, 8644), (130, 8774),
    (132, 9566), (134, 10370), (146, 11100), (152, 11708), (154, 12016),
    (160, 12976), (164, 13140), (170, 13820), (174, 14864), (178, 15220),
    (182, 15584), (184, 15952), (194, 16340),
]
X_VALUES = [x for x, _ in TOTAL_SCAP]

MODEL_LABELS = {
    "claude-opus-4.6": "Claude Opus 4.6",
    "azure/anthropic/claude-opus-5": "Claude Opus 5",
    "claude-fable-5-1": "Claude Fable 5.1",
    "gemini-3-pro-preview": "Gemini 3 Pro Preview",
    "gpt-4.1": "GPT-4.1",
    "gpt5.2": "GPT-5.2",
    "gpt-5.6-sol": "GPT-5.6 Sol",
}
MODEL_ALIASES = {
    "openai/openai/gpt-5.6-sol": "gpt-5.6-sol",
}
COLORS = ["#4C72B0", "#E07B39", "#55A868", "#C44E52", "#9467BD", "#2A9D8F", "#8C564B"]
MARKERS = ["o", "s", "D", "P", "^", "X", "v"]
LINESTYLES = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 1)), (0, (1, 1))]


def load_stabilizer_counts() -> dict[str, int]:
    with (ROOT / "data" / "benchmarks.json").open() as data_file:
        return {entry["name"]: len(entry.get("generators", [])) for entry in json.load(data_file)}


def cumulative_curve(scores: list[tuple[int, float]]) -> list[tuple[int, float]]:
    return [(x, sum(score for stabilizers, score in scores if stabilizers <= x)) for x in X_VALUES]


def completed_payloads(benchmark: str):
    for path in DATA_DIRS[benchmark].rglob("*.json"):
        if benchmark != "B3" and "cleaned" in path.parts:
            continue
        try:
            with path.open() as data_file:
                payload = json.load(data_file)
        except (OSError, json.JSONDecodeError):
            continue
        metadata = payload.get("metadata", {})
        if benchmark == "B3" and "cleaned" in path.parts and isinstance(payload.get("cleaned_results"), list):
            model = path.relative_to(DATA_DIRS[benchmark]).parts[0]
            payload["metadata"] = {"model": model, "finished_at": "cleaned"}
            yield path, payload
        elif metadata.get("finished_at") and isinstance(payload.get("results"), list):
            yield path, payload


def b1_scores(payload: dict, counts: dict[str, int]) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
    scores = [
        (counts[row["code_name"]], float(counts[row["code_name"]]))
        for row in payload["results"]
        if row.get("code_name") in counts and row.get("total", 0) > 0
        and row.get("preserved") == row.get("total")
    ]
    return scores, scores


def b2_scores(payload: dict, counts: dict[str, int]) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
    capability, quality = [], []
    for row in payload["results"]:
        count = counts.get(row.get("code_name"))
        if count is None or not (row.get("valid") and row.get("better")):
            continue
        capability.append((count, float(count)))
        quality.append((count, count * optimization_proportion(
            row.get("baseline_metrics", {}), row.get("optimized_metrics", {})
        )))
    return capability, quality


def b3_scores(payload: dict, counts: dict[str, int]) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
    capability, quality = [], []
    if "cleaned_results" in payload:
        entries = [entry for item in payload["cleaned_results"] if isinstance(item, list) for entry in item]
        for entry in entries:
            count = counts.get(entry.get("code_name"))
            score = entry.get("new_best_output", {}).get("ft_score")
            if count is not None and score is not None and score > 0:
                capability.append((count, float(count)))
                quality.append((count, count * score))
        return capability, quality
    for row in payload["results"]:
        count = counts.get(row.get("code_name"))
        candidates = [row.get("best_output", {})] + row.get("generated_circuits", [])
        valid_scores = [
            candidate["ft_score"] for candidate in candidates if isinstance(candidate, dict)
            and candidate.get("all_stabilized") is True and candidate.get("ft_score") is not None
        ]
        if count is None or not valid_scores:
            continue
        best_score = max(valid_scores)
        if best_score > 0:
            capability.append((count, float(count)))
            quality.append((count, count * best_score))
    return capability, quality


def get_scores(benchmark: str, payload: dict, counts: dict[str, int]):
    if benchmark == "B1":
        return b1_scores(payload, counts)
    if benchmark == "B2":
        return b2_scores(payload, counts)
    return b3_scores(payload, counts)


def select_runs(benchmark: str, counts: dict[str, int]):
    candidates: dict[str, list[tuple[int, Path, list, list]]] = defaultdict(list)
    for path, payload in completed_payloads(benchmark):
        raw_model = payload.get("metadata", {}).get("model")
        if raw_model:
            model = canonical_model(raw_model)
            capability, quality = get_scores(benchmark, payload, counts)
            candidates[model].append((int(sum(score for _, score in capability)), path, capability, quality))

    selected = {}
    for model, runs in candidates.items():
        override = RUN_OVERRIDES[benchmark].get(model)
        if override:
            override_path = DATA_DIRS[benchmark] / override
            matches = [run for run in runs if run[1] == override_path]
            if not matches:
                raise ValueError(f"{benchmark} override for {model} was not found: {override_path}")
            selected[model] = matches[0]
        else:
            selected[model] = max(runs, key=lambda run: (run[0], run[1].name))
    return selected


def display_label(model: str) -> str:
    return MODEL_LABELS.get(model, model.rsplit("/", 1)[-1].replace("-", " ").title())


def canonical_model(model: str) -> str:
    return MODEL_ALIASES.get(model, model)


def plot_curves(output: Path, panels: list[tuple[str, str, dict]], styles: dict, show_ceiling: bool):
    fig, axes = plt.subplots(1, len(panels), figsize=(6 * len(panels), 5.5))
    axes = np.atleast_1d(axes)
    models = sorted({model for _, _, curves in panels for model in curves}, key=display_label)
    handles = labels = None
    for axis, (title, ylabel, curves) in zip(axes, panels):
        if show_ceiling:
            ceiling = [score for _, score in TOTAL_SCAP]
            axis.plot(X_VALUES, ceiling, color="gray", linestyle="--", linewidth=1.5, label="Total benchmarks", alpha=0.7)
            axis.fill_between(X_VALUES, ceiling, alpha=0.07, color="gray")
        for index, model in enumerate(models):
            points = curves.get(model)
            if not points:
                continue
            color, marker, linestyle = styles[model]
            axis.plot([x for x, _ in points], [y for _, y in points], color=color, marker=marker,
                      markersize=6, markevery=(index % 6, 6), markeredgecolor="white", markeredgewidth=0.6,
                      linestyle=linestyle, linewidth=2.2, label=display_label(model))
        axis.set_xlabel("Number of Stabilizers", fontsize=11)
        axis.set_ylabel(ylabel, fontsize=10)
        axis.set_title(title, fontsize=12, fontweight="bold")
        axis.set_xlim(0, max(X_VALUES) + 5)
        axis.yaxis.set_major_formatter(mticker.FuncFormatter(lambda value, _: f"{value:,.0f}"))
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.grid(axis="y", alpha=0.3)
        if handles is None:
            handles, labels = axis.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=min(5, len(labels)), fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {output}")


def main():
    counts = load_stabilizer_counts()
    selected = {benchmark: select_runs(benchmark, counts) for benchmark in DATA_DIRS}
    all_models = sorted(
        {model for runs in selected.values() for model in runs}, key=display_label
    )
    styles = {
        model: (
            COLORS[index % len(COLORS)],
            MARKERS[index % len(MARKERS)],
            LINESTYLES[index % len(LINESTYLES)],
        )
        for index, model in enumerate(all_models)
    }
    for benchmark, runs in selected.items():
        print(f"{benchmark} selected runs:")
        for model, (capability_score, path, _, quality) in sorted(runs.items()):
            quality_score = sum(score for _, score in quality)
            print(
                f"  {display_label(model)}: S_cap={capability_score:,}, "
                f"S_qual={quality_score:,.2f} "
                f"[{path.relative_to(DATA_DIRS[benchmark])}]"
            )
    capability_panels = [
        (benchmark, r"Cumulative $S_{\mathrm{cap}}$", {model: cumulative_curve(capability) for model, (_, _, capability, _) in selected[benchmark].items()})
        for benchmark in ("B1", "B2", "B3")
    ]
    plot_curves(OUTPUT_DIR / "combined_difficulty_curves.png", capability_panels, styles, show_ceiling=True)
    quality_panels = [
        (f"{benchmark}: {title}", r"Cumulative $S_{\mathrm{qual}}$", {model: cumulative_curve(quality) for model, (_, _, _, quality) in selected[benchmark].items()})
        for benchmark, title in (("B2", "Circuit Optimization"), ("B3", "Fault-Tolerance"))
    ]
    plot_curves(OUTPUT_DIR / "combined_quality_difficulty_curves.png", quality_panels, styles, show_ceiling=True)


if __name__ == "__main__":
    main()