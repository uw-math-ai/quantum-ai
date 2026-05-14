from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt

from ft_score_avg import RUNS, average, collect_ft_scores


OUTPUT_DIR = Path(__file__).resolve().parent / "diagrams"


def generate_histogram(title: str, model_files: dict[str, Path], output_path: Path) -> None:
    labels: list[str] = []
    averages: list[float] = []
    counts: list[int] = []

    for label, cleaned2_path in model_files.items():
        scores = [score for _, score in collect_ft_scores(cleaned2_path)]
        mean_score = average(scores)
        if mean_score is None:
            continue

        labels.append(label)
        averages.append(mean_score)
        counts.append(len(scores))
        print(f"{title} | {label}: average ft_score = {mean_score:.4f} (n={len(scores)})")

    plt.figure(figsize=(7, 5))
    bars = plt.bar(labels, averages, color=["#d97706", "#2563eb", "#059669"])
    ymax = max(averages) if averages else 1.0
    plt.xlabel("Model")
    plt.ylabel("Average ft_score")
    plt.title(title)
    plt.ylim(0, ymax * 1.18)

    for bar, value, count in zip(bars, averages, counts):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + ymax * 0.02,
            f"{value:.3f}\nn={count}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved histogram to {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for run in RUNS:
        generate_histogram(
            title=f'{run["display_date"]}_avg_ft_score',
            model_files=run["model_files"],
            output_path=OUTPUT_DIR / f'avg_ft_score_{run["date_code"]}.png',
        )


if __name__ == "__main__":
    main()
