from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt

from ft_score_avg import RUNS, average, collect_ft_scores_by_size, load_benchmark_qubits


OUTPUT_DIR = Path(__file__).resolve().parent / "diagrams"


def render_histogram(
    title: str,
    model_names: list[str],
    under_or_equal_80_averages: list[float],
    over_80_averages: list[float],
    under_or_equal_80_counts: list[int],
    over_80_counts: list[int],
    output_path: Path,
) -> None:
    x_positions = list(range(len(model_names)))
    bar_width = 0.36
    ymax = max(under_or_equal_80_averages + over_80_averages) if any(under_or_equal_80_averages + over_80_averages) else 1.0

    plt.figure(figsize=(8, 5))
    under_or_equal_80_bars = plt.bar(
        [x - bar_width / 2 for x in x_positions],
        under_or_equal_80_averages,
        width=bar_width,
        color="#1d4ed8",
        label="<=80 physical qubits",
    )
    over_80_bars = plt.bar(
        [x + bar_width / 2 for x in x_positions],
        over_80_averages,
        width=bar_width,
        color="#b91c1c",
        label=">80 physical qubits",
    )

    plt.xlabel("Model")
    plt.ylabel("Average ft_score")
    plt.title(title)
    plt.xticks(x_positions, model_names)
    plt.ylim(0, ymax * 1.2)
    plt.legend()

    for bars, counts in [
        (under_or_equal_80_bars, under_or_equal_80_counts),
        (over_80_bars, over_80_counts),
    ]:
        for bar, count in zip(bars, counts):
            value = bar.get_height()
            label = f"{value:.3f}\nn={count}" if count else "n=0"
            y = value + ymax * 0.02 if value else ymax * 0.02
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                y,
                label,
                ha="center",
                va="bottom",
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main() -> None:
    benchmark_qubits = load_benchmark_qubits()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for run in RUNS:
        missing_names: set[str] = set()
        model_names: list[str] = []
        under_or_equal_80_averages: list[float] = []
        over_80_averages: list[float] = []
        under_or_equal_80_counts: list[int] = []
        over_80_counts: list[int] = []

        for model_name, cleaned2_path in run["model_files"].items():
            over_80, under_or_equal_80, model_missing = collect_ft_scores_by_size(cleaned2_path, benchmark_qubits)
            missing_names.update(model_missing)
            model_names.append(model_name)
            under_or_equal_80_avg = average(under_or_equal_80)
            over_80_avg = average(over_80)
            under_or_equal_80_averages.append(under_or_equal_80_avg if under_or_equal_80_avg is not None else 0.0)
            over_80_averages.append(over_80_avg if over_80_avg is not None else 0.0)
            under_or_equal_80_counts.append(len(under_or_equal_80))
            over_80_counts.append(len(over_80))
            print(
                f'{run["date_code"]} | {model_name}: <=80 avg={under_or_equal_80_avg if under_or_equal_80_avg is not None else "N/A"} '
                f'(n={len(under_or_equal_80)}), >80 avg={over_80_avg if over_80_avg is not None else "N/A"} '
                f'(n={len(over_80)})'
            )

        output_path = OUTPUT_DIR / f'over80qb_avg_ft_score_{run["date_code"]}.png'
        render_histogram(
            title=f'{run["display_date"]}_over80qb_avg_ft_score',
            model_names=model_names,
            under_or_equal_80_averages=under_or_equal_80_averages,
            over_80_averages=over_80_averages,
            under_or_equal_80_counts=under_or_equal_80_counts,
            over_80_counts=over_80_counts,
            output_path=output_path,
        )
        if missing_names:
            print(f'{run["date_code"]}: missing benchmark entries for {sorted(missing_names)}')
        print(f"Saved histogram to {output_path}")


if __name__ == "__main__":
    main()
