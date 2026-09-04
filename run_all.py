#!/usr/bin/env python3
"""
Run all three benchmarks (B1, B2, B3) from a single entry point.

Each benchmark keeps its own run.py; this script just orchestrates them with
a shared, easy-to-edit config and optional command-line overrides.

Examples
--------
    # Run everything with the defaults below
    python run_all.py

    # Only B1 and B3
    python run_all.py --only B1 B3

    # Override the model + attempts for whichever benchmarks are selected
    python run_all.py --model gpt-5.2-codex --attempts 5

    # Enable B3's post-run analysis and cap B2 at 20 circuits
    python run_all.py --analyze --limit 20

    # See the exact commands without running them
    python run_all.py --dry-run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# DEFAULT CONFIG  --  edit these to change what `python run_all.py` does.
#
# Each benchmark only receives the flags its own run.py supports. Leave a
# value as None to fall back to that benchmark's own built-in default
# (e.g. its --benchmarks data file or --prompt-file).
# ---------------------------------------------------------------------------
BENCHMARKS: dict[str, dict] = {
    "B1": {  # state-prep generation
        "script": "B1/run.py",
        "model": "gpt-5.2-codex",
        "harness": "openai",
        "attempts": 10,
        "timeout": 300,
        "benchmarks": None,    # None -> B1/run.py default (data/benchmarks.json)
        "prompt_file": None,   # None -> B1/prompts/default_prompt.txt
        "output": None,        # None -> auto B1/data/<model>/<timestamp>.json
    },
    "B2": {  # circuit optimization
        "script": "B2/run.py",
        "model": "gpt-5.2-codex",
        "harness": "openai",
        "attempts": 10,
        "timeout": 300,
        "benchmarks": None,    # None -> B2/run.py default (data/circuit_dataset.jsonl)
        "prompt_file": None,
        "output": None,
        "limit": None,         # None -> all circuits
    },
    "B3": {  # fault-tolerant state-prep generation
        "script": "B3/run.py",
        "model": "gpt-5.2-codex",
        "harness": "openai",
        "attempts": 10,
        "timeout": 300,
        "benchmarks": None,    # None -> B3/run.py default (data/circuit_dataset.jsonl)
        "prompt_file": None,
        "output": None,
        "analyze": False,      # True -> also run B3's cleaned/cleaned2 analysis
    },
}

ORDER = ["B1", "B2", "B3"]


def build_command(name: str, cfg: dict) -> list[str]:
    """Translate a benchmark's config dict into a run.py command line."""
    cmd = [sys.executable, str(REPO_ROOT / cfg["script"])]

    cmd += ["--model", str(cfg["model"])]
    cmd += ["--harness", str(cfg["harness"])]
    cmd += ["--attempts", str(cfg["attempts"])]
    cmd += ["--timeout", str(cfg["timeout"])]

    if cfg.get("benchmarks") is not None:
        cmd += ["--benchmarks", str(cfg["benchmarks"])]
    if cfg.get("prompt_file") is not None:
        cmd += ["--prompt-file", str(cfg["prompt_file"])]
    if cfg.get("output") is not None:
        cmd += ["--output", str(cfg["output"])]

    # Benchmark-specific flags
    if name == "B2" and cfg.get("limit") is not None:
        cmd += ["--limit", str(cfg["limit"])]
    if name == "B3" and cfg.get("analyze"):
        cmd += ["--analyze"]

    return cmd


def apply_overrides(cfg: dict, args: argparse.Namespace) -> dict:
    """Return a copy of cfg with any CLI overrides applied."""
    merged = dict(cfg)
    if args.model is not None:
        merged["model"] = args.model
    if args.harness is not None:
        merged["harness"] = args.harness
    if args.attempts is not None:
        merged["attempts"] = args.attempts
    if args.timeout is not None:
        merged["timeout"] = args.timeout
    if args.limit is not None:
        merged["limit"] = args.limit
    if args.analyze:
        merged["analyze"] = True
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all three benchmarks (B1, B2, B3) from one place.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--only",
        nargs="+",
        choices=ORDER,
        metavar="B#",
        help="Run only the listed benchmarks (default: all of %s)" % ", ".join(ORDER),
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the model for every selected benchmark",
    )
    parser.add_argument(
        "--harness",
        choices=("openai", "anthropic", "copilot"),
        default=None,
        help="Override the provider harness for every selected benchmark",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=None,
        help="Override the attempts for every selected benchmark",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Override the timeout (seconds) for every selected benchmark",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Override B2's circuit limit (ignored by B1/B3)",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Enable B3's post-run cleaned/cleaned2 analysis",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Keep running remaining benchmarks even if one fails "
             "(default: stop on first failure)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands that would run, then exit",
    )

    args = parser.parse_args()
    selected = args.only if args.only else ORDER

    print(f"Selected benchmarks: {', '.join(selected)}\n")

    results: dict[str, int] = {}
    for name in selected:
        cfg = apply_overrides(BENCHMARKS[name], args)
        cmd = build_command(name, cfg)
        printable = " ".join(cmd)

        print("=" * 70)
        print(f"[{name}] {printable}")
        print("=" * 70)

        if args.dry_run:
            results[name] = 0
            continue

        proc = subprocess.run(cmd, cwd=str(REPO_ROOT))
        results[name] = proc.returncode

        if proc.returncode != 0:
            print(f"\n[{name}] FAILED with exit code {proc.returncode}")
            if not args.continue_on_error:
                print("Stopping (use --continue-on-error to keep going).")
                break
        else:
            print(f"\n[{name}] completed successfully")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    for name in selected:
        if name not in results:
            status = "skipped"
        elif args.dry_run:
            status = "dry-run"
        else:
            status = "ok" if results[name] == 0 else f"FAILED ({results[name]})"
        print(f"  {name}: {status}")
    print("=" * 70)

    return 0 if all(rc == 0 for rc in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
