"""
Analyze benchmark results across agents (claude-opus-4.6, gemini-3-pro-preview, gpt5.2)
for state-preparation circuit generation.

Metrics:
  - Accuracy: fraction of stabilizers preserved (success_rate) and full-solve rate
  - Performance: elapsed time per benchmark
  - Completeness: fraction of benchmarks where a circuit was returned (not timed out)
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
import statistics

DATA_DIR = Path(__file__).parent / "data"

AGENTS = {
    "claude-opus-4.6": "claude-opus-4.6",
    "gemini-3-pro-preview": "gemini-3-pro-preview",
    "gpt5.2": "gpt5.2",
}

# ── helpers ──────────────────────────────────────────────────────────────

def load_results(agent_dir: str):
    """Load all 2602*.json result files for an agent, return list of (metadata, results)."""
    runs = []
    agent_path = DATA_DIR / agent_dir
    for f in sorted(agent_path.glob("2602*.json")):
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        runs.append((f.name, data["metadata"], data["results"]))
    return runs


def config_label(meta):
    """Human-readable label for a run configuration."""
    return f"attempts={meta['attempts']}, timeout={meta['timeout']}s"


# ── per-run statistics ───────────────────────────────────────────────────

def compute_run_stats(results):
    n = len(results)
    n_completed = sum(1 for r in results if r["circuit"] is not None)
    n_perfect = sum(1 for r in results if r["success_rate"] == 1.0)
    
    success_rates = [r["success_rate"] for r in results]
    elapsed = [r["elapsed_seconds"] for r in results]
    elapsed_completed = [r["elapsed_seconds"] for r in results if r["circuit"] is not None]
    
    # Per-qubit-count breakdown
    qubit_bins = defaultdict(list)
    for r in results:
        nq = r["total"]  # number of stabilizers ≈ proxy for complexity
        qubit_bins[nq].append(r)
    
    return {
        "total_benchmarks": n,
        "completed": n_completed,
        "completion_rate": n_completed / n if n else 0,
        "perfect_solves": n_perfect,
        "perfect_rate": n_perfect / n if n else 0,
        "mean_success_rate": statistics.mean(success_rates) if success_rates else 0,
        "median_success_rate": statistics.median(success_rates) if success_rates else 0,
        "mean_elapsed": statistics.mean(elapsed) if elapsed else 0,
        "median_elapsed": statistics.median(elapsed) if elapsed else 0,
        "mean_elapsed_completed": statistics.mean(elapsed_completed) if elapsed_completed else 0,
        "total_elapsed": sum(elapsed),
    }


# ── main analysis ────────────────────────────────────────────────────────

def print_separator(char="=", width=100):
    print(char * width)


def print_header(title):
    print()
    print_separator()
    print(f"  {title}")
    print_separator()


def analyze():
    all_data = {}  # agent -> list of (filename, meta, results)
    
    for agent_name, agent_dir in AGENTS.items():
        all_data[agent_name] = load_results(agent_dir)
    
    # ── 1. Overview per agent per config ─────────────────────────────────
    print_header("1. OVERVIEW: PER-AGENT, PER-CONFIGURATION STATISTICS")
    
    # Group runs by config
    configs = {}  # (attempts, timeout) -> {agent: stats}
    for agent_name, runs in all_data.items():
        for fname, meta, results in runs:
            key = (meta["attempts"], meta["timeout"])
            if key not in configs:
                configs[key] = {}
            stats = compute_run_stats(results)
            configs[key][agent_name] = {**stats, "filename": fname}
    
    for (attempts, timeout), agent_stats in sorted(configs.items()):
        print(f"\n  Config: attempts={attempts}, timeout={timeout}s")
        print(f"  {'Agent':<25} {'Complete':>10} {'Perfect':>10} {'Avg SR':>10} {'Med SR':>10} {'Avg Time':>10} {'Med Time':>10}")
        print(f"  {'-'*23}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")
        for agent_name in AGENTS:
            if agent_name not in agent_stats:
                continue
            s = agent_stats[agent_name]
            print(f"  {agent_name:<25} "
                  f"{s['completed']:>4}/{s['total_benchmarks']:<4}  "
                  f"{s['perfect_solves']:>4}/{s['total_benchmarks']:<4}  "
                  f"{s['mean_success_rate']:>8.1%}  "
                  f"{s['median_success_rate']:>8.1%}  "
                  f"{s['mean_elapsed']:>7.1f}s  "
                  f"{s['median_elapsed']:>7.1f}s")
    
    # ── 2. Accuracy comparison across configs ────────────────────────────
    print_header("2. ACCURACY: PERFECT-SOLVE RATE BY CONFIG")
    
    print(f"\n  {'Config':<30}", end="")
    for agent_name in AGENTS:
        print(f" {agent_name:>25}", end="")
    print()
    print(f"  {'-'*28}", end="")
    for _ in AGENTS:
        print(f"  {'-'*23}", end="")
    print()
    
    for (attempts, timeout), agent_stats in sorted(configs.items()):
        label = f"att={attempts}, to={timeout}s"
        print(f"  {label:<30}", end="")
        for agent_name in AGENTS:
            if agent_name in agent_stats:
                s = agent_stats[agent_name]
                print(f" {s['perfect_rate']:>23.1%}", end="")
            else:
                print(f" {'N/A':>23}", end="")
        print()
    
    # ── 3. Completion rate ───────────────────────────────────────────────
    print_header("3. COMPLETENESS: CIRCUIT RETURNED (not timed out)")
    
    print(f"\n  {'Config':<30}", end="")
    for agent_name in AGENTS:
        print(f" {agent_name:>25}", end="")
    print()
    print(f"  {'-'*28}", end="")
    for _ in AGENTS:
        print(f"  {'-'*23}", end="")
    print()
    
    for (attempts, timeout), agent_stats in sorted(configs.items()):
        label = f"att={attempts}, to={timeout}s"
        print(f"  {label:<30}", end="")
        for agent_name in AGENTS:
            if agent_name in agent_stats:
                s = agent_stats[agent_name]
                print(f" {s['completion_rate']:>23.1%}", end="")
            else:
                print(f" {'N/A':>23}", end="")
        print()
    
    # ── 4. Performance (mean elapsed seconds) ────────────────────────────
    print_header("4. PERFORMANCE: MEAN ELAPSED TIME (seconds)")
    
    print(f"\n  {'Config':<30}", end="")
    for agent_name in AGENTS:
        print(f" {agent_name:>25}", end="")
    print()
    print(f"  {'-'*28}", end="")
    for _ in AGENTS:
        print(f"  {'-'*23}", end="")
    print()
    
    for (attempts, timeout), agent_stats in sorted(configs.items()):
        label = f"att={attempts}, to={timeout}s"
        print(f"  {label:<30}", end="")
        for agent_name in AGENTS:
            if agent_name in agent_stats:
                s = agent_stats[agent_name]
                print(f" {s['mean_elapsed']:>22.1f}s", end="")
            else:
                print(f" {'N/A':>23}", end="")
        print()
    
    # ── 5. Per-benchmark head-to-head (many attempts, long timeout) ──────
    print_header("5. HEAD-TO-HEAD: BEST CONFIG (attempts=15, timeout=900s)")
    
    best_config = (15, 900)
    if best_config in configs:
        agent_results_map = {}
        for agent_name, runs in all_data.items():
            for fname, meta, results in runs:
                if (meta["attempts"], meta["timeout"]) == best_config:
                    agent_results_map[agent_name] = {r["code_name"]: r for r in results}
        
        # Get all code names from first agent
        first_agent = list(agent_results_map.keys())[0]
        code_names = list(agent_results_map[first_agent].keys())
        
        # Count wins
        wins = {a: 0 for a in AGENTS}
        ties = 0
        
        print(f"\n  Benchmarks where agents differ (showing success_rate | elapsed):\n")
        print(f"  {'Benchmark':<50}", end="")
        for agent_name in AGENTS:
            print(f" {agent_name:>25}", end="")
        print()
        print(f"  {'-'*48}", end="")
        for _ in AGENTS:
            print(f"  {'-'*23}", end="")
        print()
        
        diffs = 0
        for cn in code_names:
            rates = {}
            times = {}
            for agent_name in AGENTS:
                if agent_name in agent_results_map and cn in agent_results_map[agent_name]:
                    r = agent_results_map[agent_name][cn]
                    rates[agent_name] = r["success_rate"]
                    times[agent_name] = r["elapsed_seconds"]
            
            # Check if they differ
            unique_rates = set(rates.values())
            if len(unique_rates) > 1:
                diffs += 1
                short_cn = cn[:48]
                print(f"  {short_cn:<50}", end="")
                for agent_name in AGENTS:
                    if agent_name in rates:
                        print(f" {rates[agent_name]:>11.0%} | {times[agent_name]:>7.1f}s", end="")
                    else:
                        print(f" {'N/A':>23}", end="")
                print()
            
            # Determine winner by success_rate, then by time
            if rates:
                best_rate = max(rates.values())
                best_agents = [a for a, r in rates.items() if r == best_rate]
                if len(best_agents) == 1:
                    wins[best_agents[0]] += 1
                elif len(best_agents) > 1:
                    # Tiebreak by time
                    best_time_agent = min(best_agents, key=lambda a: times.get(a, float('inf')))
                    wins[best_time_agent] += 1
        
        if diffs == 0:
            print("  (All benchmarks have identical success rates across agents)")
        
        print(f"\n  Win counts (best success_rate, tiebreak by speed):")
        for agent_name in AGENTS:
            print(f"    {agent_name:<25}: {wins[agent_name]:>4} / {len(code_names)}")
    
    # ── 6. Difficulty analysis ───────────────────────────────────────────
    print_header("6. DIFFICULTY ANALYSIS: SUCCESS RATE BY STABILIZER COUNT")
    
    # Use the best config for this
    best_config = (15, 900)
    if best_config in configs:
        agent_results_map = {}
        for agent_name, runs in all_data.items():
            for fname, meta, results in runs:
                if (meta["attempts"], meta["timeout"]) == best_config:
                    agent_results_map[agent_name] = results
        
        # Define bins by total stabilizers
        bins = [(1, 4), (5, 10), (11, 20), (21, 50), (51, 100), (101, 200)]
        
        print(f"\n  {'Stab. range':<15}", end="")
        for agent_name in AGENTS:
            print(f" {agent_name + ' (perf/tot)':>30}", end="")
        print()
        print(f"  {'-'*13}", end="")
        for _ in AGENTS:
            print(f"  {'-'*28}", end="")
        print()
        
        for lo, hi in bins:
            print(f"  {lo:>3}-{hi:<4}       ", end="")
            for agent_name in AGENTS:
                if agent_name in agent_results_map:
                    subset = [r for r in agent_results_map[agent_name] if lo <= r["total"] <= hi]
                    if subset:
                        perfect = sum(1 for r in subset if r["success_rate"] == 1.0)
                        avg_sr = statistics.mean([r["success_rate"] for r in subset])
                        print(f" {perfect:>4}/{len(subset):<4} (avg {avg_sr:.0%}){' ':>6}", end="")
                    else:
                        print(f" {'--':>28}", end="")
            print()
    
    # ── 7. Failure analysis ──────────────────────────────────────────────
    print_header("7. FAILURE ANALYSIS: BENCHMARKS FAILED BY ALL AGENTS (best config)")
    
    best_config = (15, 900)
    if best_config in configs:
        agent_results_map = {}
        for agent_name, runs in all_data.items():
            for fname, meta, results in runs:
                if (meta["attempts"], meta["timeout"]) == best_config:
                    agent_results_map[agent_name] = {r["code_name"]: r for r in results}
        
        first_agent = list(agent_results_map.keys())[0]
        code_names = list(agent_results_map[first_agent].keys())
        
        all_fail = []
        for cn in code_names:
            all_imperfect = True
            for agent_name in AGENTS:
                if agent_name in agent_results_map and cn in agent_results_map[agent_name]:
                    if agent_results_map[agent_name][cn]["success_rate"] == 1.0:
                        all_imperfect = False
                        break
            if all_imperfect:
                row = {"code_name": cn}
                for agent_name in AGENTS:
                    if agent_name in agent_results_map and cn in agent_results_map[agent_name]:
                        r = agent_results_map[agent_name][cn]
                        row[agent_name] = f"{r['preserved']}/{r['total']} ({r['success_rate']:.0%})"
                all_fail.append(row)
        
        if all_fail:
            print(f"\n  Found {len(all_fail)} benchmarks unsolved by any agent:\n")
            print(f"  {'Benchmark':<50}", end="")
            for agent_name in AGENTS:
                print(f" {agent_name:>25}", end="")
            print()
            print(f"  {'-'*48}", end="")
            for _ in AGENTS:
                print(f"  {'-'*23}", end="")
            print()
            for row in all_fail:
                short_cn = row["code_name"][:48]
                print(f"  {short_cn:<50}", end="")
                for agent_name in AGENTS:
                    print(f" {row.get(agent_name, 'N/A'):>23}", end="")
                print()
        else:
            print("\n  All benchmarks were perfectly solved by at least one agent!")
    
    # ── 8. Impact of attempts and timeout ────────────────────────────────
    print_header("8. IMPACT OF CONFIGURATION (attempts / timeout)")
    
    for agent_name in AGENTS:
        runs = all_data[agent_name]
        print(f"\n  {agent_name}:")
        print(f"  {'Config':<35} {'Perfect':>10} {'Completed':>12} {'Avg SR':>10} {'Avg Time':>10}")
        print(f"  {'-'*33}  {'-'*8}  {'-'*10}  {'-'*8}  {'-'*8}")
        for fname, meta, results in sorted(runs, key=lambda x: (x[1]["attempts"], x[1]["timeout"])):
            stats = compute_run_stats(results)
            label = config_label(meta)
            print(f"  {label:<35} "
                  f"{stats['perfect_solves']:>4}/{stats['total_benchmarks']:<4}  "
                  f"{stats['completed']:>4}/{stats['total_benchmarks']:<6}  "
                  f"{stats['mean_success_rate']:>8.1%}  "
                  f"{stats['mean_elapsed']:>7.1f}s")

    # ── 9. Overall ranking ───────────────────────────────────────────────
    print_header("9. OVERALL RANKING")
    
    # Aggregate across all configs
    agent_agg = {a: {"perfect": 0, "total": 0, "completed": 0, "sum_sr": 0, "sum_time": 0, "count": 0}
                 for a in AGENTS}
    
    for (attempts, timeout), agent_stats in configs.items():
        for agent_name in AGENTS:
            if agent_name in agent_stats:
                s = agent_stats[agent_name]
                agent_agg[agent_name]["perfect"] += s["perfect_solves"]
                agent_agg[agent_name]["total"] += s["total_benchmarks"]
                agent_agg[agent_name]["completed"] += s["completed"]
                agent_agg[agent_name]["sum_sr"] += s["mean_success_rate"] * s["total_benchmarks"]
                agent_agg[agent_name]["sum_time"] += s["total_elapsed"]
                agent_agg[agent_name]["count"] += s["total_benchmarks"]
    
    ranking = []
    for agent_name in AGENTS:
        a = agent_agg[agent_name]
        ranking.append({
            "agent": agent_name,
            "perfect_rate": a["perfect"] / a["total"] if a["total"] else 0,
            "completion_rate": a["completed"] / a["total"] if a["total"] else 0,
            "avg_sr": a["sum_sr"] / a["count"] if a["count"] else 0,
            "avg_time": a["sum_time"] / a["count"] if a["count"] else 0,
        })
    
    # Sort by: perfect_rate desc, avg_sr desc, avg_time asc
    ranking.sort(key=lambda x: (-x["perfect_rate"], -x["avg_sr"], x["avg_time"]))
    
    print(f"\n  Aggregated across all 3 configurations ({len(configs)} configs × 192 benchmarks):\n")
    print(f"  {'Rank':<6} {'Agent':<25} {'Perfect Rate':>14} {'Completion':>12} {'Avg SR':>10} {'Avg Time':>10}")
    print(f"  {'-'*4}  {'-'*23}  {'-'*12}  {'-'*10}  {'-'*8}  {'-'*8}")
    for i, r in enumerate(ranking, 1):
        print(f"  {i:<6} {r['agent']:<25} {r['perfect_rate']:>12.1%}  {r['completion_rate']:>10.1%}  {r['avg_sr']:>8.1%}  {r['avg_time']:>7.1f}s")
    
    print()
    print_separator()
    print(f"  WINNER: {ranking[0]['agent']}")
    print_separator()
    print()


if __name__ == "__main__":
    analyze()
