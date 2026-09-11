"""Generate markdown tables comparing every completed run, grouped by model.

Mirrors Tables II-IV in ieee-paper.pdf (config, success/perfect-solve rate,
S_cap, S_qual) but lists every completed run under B1/data, B2/data, and
B3/data instead of only the paper's baseline runs. Reuses the capability
and quality scoring already established in plot_combined_difficulty_curves.py
(B1/B2/B3 S_cap/S_qual) and analyze_models.py (B2 success rate, mean 2Q-gate
reduction) so the numbers stay consistent with the rest of analysis/.

Usage:
    python analysis/generate_run_tables.py

Output:
    analysis/tables.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "B2"))
from analyze_models import extract_stats  # noqa: E402
from plot_combined_difficulty_curves import (  # noqa: E402
    DATA_DIRS,
    canonical_model,
    completed_payloads,
    display_label,
    get_scores,
    load_stabilizer_counts,
)

OUTPUT_PATH = Path(__file__).resolve().parent / "tables.md"

# B3's legacy "cleaned" runs (claude-opus-4.6, gemini-3-pro-preview, gpt5.2)
# predate this repo's metadata logging, so their attempts/timeout/prompt are
# not recoverable from the JSON. The config label below is recovered from
# ieee-paper.pdf Table IV by matching each date-stamped run's S_cap.
B3_LEGACY_CONFIG_BY_DATE = {
    "260314": "prompt a / 15 att / 300s",
    "260319": "prompt b / 15 att / 300s",
    "260320": "prompt b / 15 att / 900s",
    "260321": "prompt b / 1 att / 900s",
}


def prompt_stem(prompt_path: str | None) -> str:
    return Path(prompt_path.replace("\\", "/")).stem if prompt_path else "?"


def config_label(benchmark: str, path: Path, payload: dict) -> str:
    metadata = payload.get("metadata", {})
    if benchmark == "B3" and metadata.get("finished_at") == "cleaned":
        return B3_LEGACY_CONFIG_BY_DATE.get(path.stem.split(".")[0], f"cleaned ({path.stem})")

    attempts = metadata.get("attempts", metadata.get("max_attempts"))
    timeout = metadata.get("timeout")
    prompt = prompt_stem(metadata.get("prompt_path"))
    return f"{attempts} att / {timeout}s ({prompt})"


def num_codes(benchmark: str, payload: dict) -> int:
    if benchmark == "B3" and payload.get("metadata", {}).get("finished_at") == "cleaned":
        return sum(len(item) for item in payload["cleaned_results"] if isinstance(item, list))
    return len(payload.get("results", []))


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def fmt_score(value: float) -> str:
    return f"{value:,.0f}"


def collect_rows(benchmark: str, counts: dict[str, int]) -> dict[str, list[dict]]:
    rows_by_model: dict[str, list[dict]] = {}
    for path, payload in completed_payloads(benchmark):
        raw_model = payload.get("metadata", {}).get("model")
        if not raw_model:
            continue
        model = canonical_model(raw_model)
        capability, quality = get_scores(benchmark, payload, counts)
        s_cap = sum(score for _, score in capability)
        s_qual = sum(score for _, score in quality)
        codes = num_codes(benchmark, payload)
        n_success = len(capability)

        row = {
            "model": model,
            "run": path.stem,
            "config": config_label(benchmark, path, payload),
            "codes": codes,
            "success_rate": (n_success / codes * 100) if codes else 0.0,
            "s_cap": s_cap,
            "s_qual": s_qual,
        }
        if benchmark == "B2":
            stats = extract_stats(payload, counts)
            row["success_rate"] = stats["success_rate"]
            row["mean_g2q"] = stats["mean_cx_red"]
        rows_by_model.setdefault(model, []).append(row)
    return rows_by_model


def render_table(benchmark: str, rows_by_model: dict[str, list[dict]]) -> str:
    lines = []
    if benchmark == "B1":
        header = "| Model | Run | Config | Codes | Perfect Solve Rate | S_cap |"
        sep = "|---|---|---|---|---|---|"
    elif benchmark == "B2":
        header = "| Model | Run | Config | Codes | Success Rate | S_cap | S_qual | Mean 2Q-gate reduction |"
        sep = "|---|---|---|---|---|---|---|---|"
    else:
        header = "| Model | Run | Config | Codes | Success Rate | S_cap | S_qual |"
        sep = "|---|---|---|---|---|---|---|"

    lines.append(header)
    lines.append(sep)
    all_rows = [row for rows in rows_by_model.values() for row in rows]
    for row in sorted(all_rows, key=lambda r: r["run"]):
        model_label = display_label(row["model"])
        if benchmark == "B2":
            lines.append(
                f"| {model_label} | {row['run']} | {row['config']} | {row['codes']} "
                f"| {fmt_pct(row['success_rate'])} | {fmt_score(row['s_cap'])} | {fmt_score(row['s_qual'])} "
                f"| {fmt_pct(row['mean_g2q'])} |"
            )
        elif benchmark == "B3":
            lines.append(
                f"| {model_label} | {row['run']} | {row['config']} | {row['codes']} "
                f"| {fmt_pct(row['success_rate'])} | {fmt_score(row['s_cap'])} | {fmt_score(row['s_qual'])} |"
            )
        else:
            lines.append(
                f"| {model_label} | {row['run']} | {row['config']} | {row['codes']} "
                f"| {fmt_pct(row['success_rate'])} | {fmt_score(row['s_cap'])} |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    counts = load_stabilizer_counts()
    total_stabilizers = sum(counts.values())

    sections = []
    sections.append("# Run Comparison\n")
    sections.append(
        "Every completed run under `B1/data`, `B2/data`, and `B3/data`, sorted by run ID. "
        f"Scores follow the same S_cap/S_qual definitions as `plot_combined_difficulty_curves.py` "
        f"(max possible S_cap = {total_stabilizers:,}). Compare against Tables II-IV in "
        "`ieee-paper.pdf` for the paper's baseline-run subset.\n"
    )

    sections.append("## B1: State-Preparation Circuit Synthesis\n")
    sections.append(render_table("B1", collect_rows("B1", counts)))

    sections.append("## B2: Circuit Optimization\n")
    sections.append(render_table("B2", collect_rows("B2", counts)))

    sections.append("## B3: Fault-Tolerant Circuit Generation\n")
    sections.append(
        "Note: B3's \"cleaned\" legacy runs (claude-opus-4.6, gemini-3-pro-preview, gpt5.2) "
        "don't retain per-run metadata, so their config labels are recovered by matching S_cap "
        "against ieee-paper.pdf Table IV.\n"
    )
    sections.append(render_table("B3", collect_rows("B3", counts)))

    OUTPUT_PATH.write_text("\n".join(sections) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
