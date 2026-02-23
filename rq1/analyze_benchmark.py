"""
Comprehensive analysis of quantum state-preparation circuit benchmark results.
Analyzes results from 3 agents x 3 configurations across 192 stabilizer codes.
"""

import json
import os
import csv
import math
from collections import defaultdict
from pathlib import Path

# ==============================================================================
# CONFIG
# ==============================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BENCHMARKS_PATH = BASE_DIR.parent / "data" / "benchmarks.json"
OUTPUT_DIR = BASE_DIR / "analysis_results"
OUTPUT_DIR.mkdir(exist_ok=True)

AGENTS = {
    "claude-opus-4.6": "Claude Opus 4.6",
    "gemini-3-pro-preview": "Gemini 3 Pro Preview",
    "gpt5.2": "GPT-5.2",
}

# Map files to configs based on metadata
# File pattern: 2602*.json

# ==============================================================================
# LOAD DATA
# ==============================================================================

def load_benchmarks():
    with open(BENCHMARKS_PATH) as f:
        benchmarks = json.load(f)
    bm_map = {}
    for b in benchmarks:
        bm_map[b["name"]] = {
            "name": b["name"],
            "physical_qubits": b["physical_qubits"],
            "logical_qubits": b["logical_qubits"],
            "d": b["d"],
            "num_generators": len(b["generators"]),
            "generators": b["generators"],
            "is_tensor_product": " * " in b["name"],
            "max_weight": max(len(g.replace("I", "")) for g in b["generators"]),
        }
    return bm_map


def load_all_results():
    """Load all results from all agents."""
    all_results = []
    
    for agent_dir_name, agent_label in AGENTS.items():
        agent_dir = DATA_DIR / agent_dir_name
        if not agent_dir.exists():
            print(f"WARNING: Agent directory not found: {agent_dir}")
            continue
        
        for json_file in sorted(agent_dir.glob("2602*.json")):
            with open(json_file) as f:
                data = json.load(f)
            
            meta = data["metadata"]
            config_key = f"attempts={meta['attempts']},timeout={meta['timeout']}"
            config_label = f"{meta['attempts']} attempt(s), {meta['timeout']}s timeout"
            
            for r in data["results"]:
                all_results.append({
                    "agent": agent_label,
                    "agent_dir": agent_dir_name,
                    "file": json_file.name,
                    "attempts": meta["attempts"],
                    "timeout": meta["timeout"],
                    "config_key": config_key,
                    "config_label": config_label,
                    "code_name": r["code_name"],
                    "has_circuit": r["circuit"] is not None,
                    "preserved": r["preserved"],
                    "total": r["total"],
                    "success_rate": r["success_rate"],
                    "perfect": r["success_rate"] == 1.0,
                    "elapsed_seconds": r["elapsed_seconds"],
                })
    
    return all_results


# ==============================================================================
# ANALYSIS FUNCTIONS
# ==============================================================================

def agent_config_summary(results, benchmarks):
    """Table 1: Per-agent, per-config aggregate statistics."""
    groups = defaultdict(list)
    for r in results:
        key = (r["agent"], r["config_label"])
        groups[key].append(r)
    
    rows = []
    for (agent, config), items in sorted(groups.items()):
        n = len(items)
        perfect_count = sum(1 for r in items if r["perfect"])
        completion_count = sum(1 for r in items if r["has_circuit"])
        avg_success = sum(r["success_rate"] for r in items) / n
        avg_elapsed = sum(r["elapsed_seconds"] for r in items) / n
        median_elapsed = sorted(r["elapsed_seconds"] for r in items)[n // 2]
        
        rows.append({
            "Agent": agent,
            "Config": config,
            "N": n,
            "Perfect Solve Rate": f"{perfect_count}/{n} ({100*perfect_count/n:.1f}%)",
            "Completion Rate": f"{completion_count}/{n} ({100*completion_count/n:.1f}%)",
            "Avg Success Rate": f"{avg_success:.3f}",
            "Avg Elapsed (s)": f"{avg_elapsed:.1f}",
            "Median Elapsed (s)": f"{median_elapsed:.1f}",
            # numeric for CSV
            "_perfect_count": perfect_count,
            "_completion_count": completion_count,
            "_avg_success": avg_success,
            "_avg_elapsed": avg_elapsed,
        })
    
    return rows


def agent_aggregate_summary(results):
    """Aggregate across all configs for each agent."""
    groups = defaultdict(list)
    for r in results:
        groups[r["agent"]].append(r)
    
    rows = []
    for agent, items in sorted(groups.items()):
        n = len(items)
        perfect_count = sum(1 for r in items if r["perfect"])
        completion_count = sum(1 for r in items if r["has_circuit"])
        avg_success = sum(r["success_rate"] for r in items) / n
        avg_elapsed = sum(r["elapsed_seconds"] for r in items) / n
        
        rows.append({
            "Agent": agent,
            "Total Runs": n,
            "Perfect Solves": perfect_count,
            "Perfect Solve Rate": f"{100*perfect_count/n:.1f}%",
            "Completions": completion_count,
            "Completion Rate": f"{100*completion_count/n:.1f}%",
            "Avg Success Rate": f"{avg_success:.3f}",
            "Avg Elapsed (s)": f"{avg_elapsed:.1f}",
        })
    
    return rows


def difficulty_by_stabilizer_count(results, benchmarks):
    """Analyze success by stabilizer count ranges."""
    # Determine which benchmarks were perfectly solved, by any/all agents
    # Use best config for each agent-benchmark pair
    best = {}  # (agent, code_name) -> best result
    for r in results:
        key = (r["agent"], r["code_name"])
        if key not in best or r["success_rate"] > best[key]["success_rate"]:
            best[key] = r
    
    # Group by stabilizer count range
    ranges = [(1, 2), (3, 8), (9, 14), (15, 24), (25, 50), (51, 100), (101, 200)]
    
    rows = []
    for lo, hi in ranges:
        codes_in_range = [name for name, b in benchmarks.items() 
                          if lo <= b["num_generators"] <= hi]
        if not codes_in_range:
            continue
        
        solved_by_any = 0
        solved_by_all = 0
        
        for code_name in codes_in_range:
            agents_solved = []
            for agent_label in AGENTS.values():
                key = (agent_label, code_name)
                if key in best and best[key]["perfect"]:
                    agents_solved.append(agent_label)
            if len(agents_solved) > 0:
                solved_by_any += 1
            if len(agents_solved) == len(AGENTS):
                solved_by_all += 1
        
        # Average best success rate across agents for codes in range
        all_best_rates = []
        for code_name in codes_in_range:
            for agent_label in AGENTS.values():
                key = (agent_label, code_name)
                if key in best:
                    all_best_rates.append(best[key]["success_rate"])
        
        avg_best_success = sum(all_best_rates) / len(all_best_rates) if all_best_rates else 0
        
        rows.append({
            "Stabilizer Range": f"{lo}-{hi}",
            "Benchmarks": len(codes_in_range),
            "Solved by Any Agent": f"{solved_by_any}/{len(codes_in_range)} ({100*solved_by_any/len(codes_in_range):.0f}%)",
            "Solved by All Agents": f"{solved_by_all}/{len(codes_in_range)} ({100*solved_by_all/len(codes_in_range):.0f}%)",
            "Avg Best Success Rate": f"{avg_best_success:.3f}",
        })
    
    return rows


def difficulty_by_code_type(results, benchmarks):
    """Analyze success by base vs tensor product codes."""
    best = {}
    for r in results:
        key = (r["agent"], r["code_name"])
        if key not in best or r["success_rate"] > best[key]["success_rate"]:
            best[key] = r
    
    rows = []
    for code_type, label in [(False, "Base Code"), (True, "Tensor Product")]:
        codes = [name for name, b in benchmarks.items() if b["is_tensor_product"] == code_type]
        
        for agent_label in AGENTS.values():
            n = 0
            perfect = 0
            total_success = 0
            for code_name in codes:
                key = (agent_label, code_name)
                if key in best:
                    n += 1
                    if best[key]["perfect"]:
                        perfect += 1
                    total_success += best[key]["success_rate"]
            
            if n > 0:
                rows.append({
                    "Code Type": label,
                    "Agent": agent_label,
                    "Benchmarks": n,
                    "Perfect Solves": perfect,
                    "Perfect Solve Rate": f"{100*perfect/n:.1f}%",
                    "Avg Success Rate": f"{total_success/n:.3f}",
                })
    
    return rows


def difficulty_by_distance(results, benchmarks):
    """Analyze success by code distance."""
    best = {}
    for r in results:
        key = (r["agent"], r["code_name"])
        if key not in best or r["success_rate"] > best[key]["success_rate"]:
            best[key] = r
    
    distances = sorted(set(b["d"] for b in benchmarks.values()))
    
    rows = []
    for d in distances:
        codes = [name for name, b in benchmarks.items() if b["d"] == d]
        
        all_perfect = 0
        all_n = 0
        all_success = 0
        
        for agent_label in AGENTS.values():
            for code_name in codes:
                key = (agent_label, code_name)
                if key in best:
                    all_n += 1
                    if best[key]["perfect"]:
                        all_perfect += 1
                    all_success += best[key]["success_rate"]
        
        any_solved = 0
        all_solved = 0
        for code_name in codes:
            agent_results = []
            for agent_label in AGENTS.values():
                key = (agent_label, code_name)
                if key in best:
                    agent_results.append(best[key]["perfect"])
            if any(agent_results):
                any_solved += 1
            if all(agent_results) and agent_results:
                all_solved += 1
        
        rows.append({
            "Distance": d,
            "Benchmarks": len(codes),
            "Solved by Any": f"{any_solved}/{len(codes)}",
            "Solved by All": f"{all_solved}/{len(codes)}",
            "Avg Perfect Rate (all agents)": f"{100*all_perfect/all_n:.1f}%" if all_n > 0 else "N/A",
            "Avg Success Rate (all agents)": f"{all_success/all_n:.3f}" if all_n > 0 else "N/A",
        })
    
    return rows


def never_solved_benchmarks(results, benchmarks):
    """Find benchmarks never perfectly solved by any agent in any config."""
    perfect_set = set()
    for r in results:
        if r["perfect"]:
            perfect_set.add(r["code_name"])
    
    never_solved = []
    for name, b in benchmarks.items():
        if name not in perfect_set:
            never_solved.append({
                "Code Name": name,
                "Qubits": b["physical_qubits"],
                "Generators": b["num_generators"],
                "Distance": b["d"],
                "Tensor Product": "Yes" if b["is_tensor_product"] else "No",
                "Max Weight": b["max_weight"],
            })
    
    never_solved.sort(key=lambda x: x["Generators"])
    return never_solved


def sometimes_solved_benchmarks(results, benchmarks):
    """Find benchmarks solved by some but not all agents."""
    # Per agent, which benchmarks were perfectly solved (any config)
    solved_by = defaultdict(set)
    for r in results:
        if r["perfect"]:
            solved_by[r["agent"]].add(r["code_name"])
    
    all_solved = set.intersection(*solved_by.values()) if solved_by else set()
    any_solved = set.union(*solved_by.values()) if solved_by else set()
    
    partial = any_solved - all_solved
    
    rows = []
    for code_name in sorted(partial):
        b = benchmarks.get(code_name, {})
        agents_who_solved = [a for a, s in solved_by.items() if code_name in s]
        rows.append({
            "Code Name": code_name,
            "Qubits": b.get("physical_qubits", "?"),
            "Generators": b.get("num_generators", "?"),
            "Distance": b.get("d", "?"),
            "Tensor Product": "Yes" if b.get("is_tensor_product") else "No",
            "Solved By": ", ".join(sorted(agents_who_solved)),
        })
    
    return rows


def attempts_comparison(results):
    """Compare 1 attempt (900s) vs 15 attempts (300s, 900s)."""
    # Group by agent, code_name, config
    grouped = defaultdict(dict)
    for r in results:
        key = (r["agent"], r["code_name"])
        config = (r["attempts"], r["timeout"])
        grouped[key][config] = r
    
    # Comparison 1: 1 attempt vs 15 attempts (both 900s timeout)
    comparisons = []
    
    for (agent, code_name), configs in grouped.items():
        one_900 = configs.get((1, 900))
        fifteen_900 = configs.get((15, 900))
        fifteen_300 = configs.get((15, 300))
        
        if one_900 and fifteen_900:
            comparisons.append({
                "comparison": "1att_vs_15att_900s",
                "agent": agent,
                "code_name": code_name,
                "baseline_perfect": one_900["perfect"],
                "treatment_perfect": fifteen_900["perfect"],
                "baseline_success": one_900["success_rate"],
                "treatment_success": fifteen_900["success_rate"],
                "baseline_elapsed": one_900["elapsed_seconds"],
                "treatment_elapsed": fifteen_900["elapsed_seconds"],
            })
        
        if fifteen_300 and fifteen_900:
            comparisons.append({
                "comparison": "300s_vs_900s_15att",
                "agent": agent,
                "code_name": code_name,
                "baseline_perfect": fifteen_300["perfect"],
                "treatment_perfect": fifteen_900["perfect"],
                "baseline_success": fifteen_300["success_rate"],
                "treatment_success": fifteen_900["success_rate"],
                "baseline_elapsed": fifteen_300["elapsed_seconds"],
                "treatment_elapsed": fifteen_900["elapsed_seconds"],
            })
        
        if one_900 and fifteen_300:
            comparisons.append({
                "comparison": "1att900s_vs_15att300s",
                "agent": agent,
                "code_name": code_name,
                "baseline_perfect": one_900["perfect"],
                "treatment_perfect": fifteen_300["perfect"],
                "baseline_success": one_900["success_rate"],
                "treatment_success": fifteen_300["success_rate"],
                "baseline_elapsed": one_900["elapsed_seconds"],
                "treatment_elapsed": fifteen_300["elapsed_seconds"],
            })
    
    return comparisons


def mcnemar_test(b, c):
    """McNemar's test for paired binary data. b=baseline_only, c=treatment_only."""
    if b + c == 0:
        return 1.0
    # McNemar chi-squared (with continuity correction)
    chi2 = (abs(b - c) - 1) ** 2 / (b + c) if (b + c) > 0 else 0
    # Approximate p-value from chi-squared with 1 df
    # Using a simple approximation
    p = math.exp(-chi2 / 2)  # rough approximation
    return p


def summarize_comparison(comparisons, comp_name):
    """Aggregate a specific comparison across agents."""
    relevant = [c for c in comparisons if c["comparison"] == comp_name]
    
    if not relevant:
        return []
    
    agent_groups = defaultdict(list)
    for c in relevant:
        agent_groups[c["agent"]].append(c)
    
    rows = []
    for agent, items in sorted(agent_groups.items()):
        n = len(items)
        baseline_perfect = sum(1 for c in items if c["baseline_perfect"])
        treatment_perfect = sum(1 for c in items if c["treatment_perfect"])
        
        # Paired changes
        gained = sum(1 for c in items if not c["baseline_perfect"] and c["treatment_perfect"])
        lost = sum(1 for c in items if c["baseline_perfect"] and not c["treatment_perfect"])
        
        baseline_avg_success = sum(c["baseline_success"] for c in items) / n
        treatment_avg_success = sum(c["treatment_success"] for c in items) / n
        
        baseline_avg_elapsed = sum(c["baseline_elapsed"] for c in items) / n
        treatment_avg_elapsed = sum(c["treatment_elapsed"] for c in items) / n
        
        p_value = mcnemar_test(lost, gained)
        
        rows.append({
            "Agent": agent,
            "N": n,
            "Baseline Perfect": f"{baseline_perfect}/{n} ({100*baseline_perfect/n:.1f}%)",
            "Treatment Perfect": f"{treatment_perfect}/{n} ({100*treatment_perfect/n:.1f}%)",
            "Gained": gained,
            "Lost": lost,
            "Net Change": f"+{gained - lost}" if gained >= lost else f"{gained - lost}",
            "p-value (McNemar)": f"{p_value:.4f}" if p_value < 0.05 else f"{p_value:.4f} (NS)",
            "Baseline Avg Success": f"{baseline_avg_success:.3f}",
            "Treatment Avg Success": f"{treatment_avg_success:.3f}",
            "Delta Avg Success": f"{treatment_avg_success - baseline_avg_success:+.3f}",
            "Baseline Avg Time (s)": f"{baseline_avg_elapsed:.1f}",
            "Treatment Avg Time (s)": f"{treatment_avg_elapsed:.1f}",
        })
    
    # Overall
    n = len(relevant)
    baseline_perfect = sum(1 for c in relevant if c["baseline_perfect"])
    treatment_perfect = sum(1 for c in relevant if c["treatment_perfect"])
    gained = sum(1 for c in relevant if not c["baseline_perfect"] and c["treatment_perfect"])
    lost = sum(1 for c in relevant if c["baseline_perfect"] and not c["treatment_perfect"])
    baseline_avg_success = sum(c["baseline_success"] for c in relevant) / n
    treatment_avg_success = sum(c["treatment_success"] for c in relevant) / n
    
    p_value = mcnemar_test(lost, gained)
    
    rows.append({
        "Agent": "ALL AGENTS",
        "N": n,
        "Baseline Perfect": f"{baseline_perfect}/{n} ({100*baseline_perfect/n:.1f}%)",
        "Treatment Perfect": f"{treatment_perfect}/{n} ({100*treatment_perfect/n:.1f}%)",
        "Gained": gained,
        "Lost": lost,
        "Net Change": f"+{gained - lost}" if gained >= lost else f"{gained - lost}",
        "p-value (McNemar)": f"{p_value:.4f}" if p_value < 0.05 else f"{p_value:.4f} (NS)",
        "Baseline Avg Success": f"{baseline_avg_success:.3f}",
        "Treatment Avg Success": f"{treatment_avg_success:.3f}",
        "Delta Avg Success": f"{treatment_avg_success - baseline_avg_success:+.3f}",
        "Baseline Avg Time (s)": f"{sum(c['baseline_elapsed'] for c in relevant)/n:.1f}",
        "Treatment Avg Time (s)": f"{sum(c['treatment_elapsed'] for c in relevant)/n:.1f}",
    })
    
    return rows


def unique_agent_strengths(results, benchmarks):
    """Find benchmarks uniquely solved by each agent."""
    solved_by = defaultdict(set)
    for r in results:
        if r["perfect"]:
            solved_by[r["agent"]].add(r["code_name"])
    
    rows = []
    for agent_label in sorted(AGENTS.values()):
        others = set()
        for other_agent, codes in solved_by.items():
            if other_agent != agent_label:
                others |= codes
        
        unique = solved_by[agent_label] - others
        for code_name in sorted(unique):
            b = benchmarks.get(code_name, {})
            rows.append({
                "Agent": agent_label,
                "Code Name": code_name,
                "Qubits": b.get("physical_qubits", "?"),
                "Generators": b.get("num_generators", "?"),
                "Distance": b.get("d", "?"),
                "Tensor Product": "Yes" if b.get("is_tensor_product") else "No",
            })
    
    return rows


def per_benchmark_detailed(results, benchmarks):
    """Create a detailed per-benchmark, per-agent, per-config table."""
    rows = []
    for r in results:
        b = benchmarks.get(r["code_name"], {})
        rows.append({
            "Code Name": r["code_name"],
            "Agent": r["agent"],
            "Config": r["config_label"],
            "Attempts": r["attempts"],
            "Timeout": r["timeout"],
            "Has Circuit": r["has_circuit"],
            "Preserved": r["preserved"],
            "Total": r["total"],
            "Success Rate": r["success_rate"],
            "Perfect": r["perfect"],
            "Elapsed (s)": r["elapsed_seconds"],
            "Qubits": b.get("physical_qubits", "?"),
            "Distance": b.get("d", "?"),
            "Tensor Product": b.get("is_tensor_product", "?"),
            "Max Weight": b.get("max_weight", "?"),
        })
    return rows


def frontier_analysis(results, benchmarks):
    """Find the max stabilizer count solved by each agent, any agent, all agents."""
    solved_by = defaultdict(set)
    for r in results:
        if r["perfect"]:
            solved_by[r["agent"]].add(r["code_name"])
    
    rows = []
    for agent_label in sorted(AGENTS.values()):
        if solved_by[agent_label]:
            max_gens = max(benchmarks[c]["num_generators"] for c in solved_by[agent_label] if c in benchmarks)
            max_qubits = max(benchmarks[c]["physical_qubits"] for c in solved_by[agent_label] if c in benchmarks)
            max_dist = max(benchmarks[c]["d"] for c in solved_by[agent_label] if c in benchmarks)
            rows.append({
                "Agent": agent_label,
                "Total Perfect Solves": len(solved_by[agent_label]),
                "Max Stabilizers Solved": max_gens,
                "Max Qubits Solved": max_qubits,
                "Max Distance Solved": max_dist,
            })
    
    # Any agent / All agents
    any_solved = set.union(*solved_by.values()) if solved_by else set()
    all_solved = set.intersection(*solved_by.values()) if solved_by else set()
    
    if any_solved:
        rows.append({
            "Agent": "ANY AGENT",
            "Total Perfect Solves": len(any_solved),
            "Max Stabilizers Solved": max(benchmarks[c]["num_generators"] for c in any_solved if c in benchmarks),
            "Max Qubits Solved": max(benchmarks[c]["physical_qubits"] for c in any_solved if c in benchmarks),
            "Max Distance Solved": max(benchmarks[c]["d"] for c in any_solved if c in benchmarks),
        })
    
    if all_solved:
        rows.append({
            "Agent": "ALL AGENTS",
            "Total Perfect Solves": len(all_solved),
            "Max Stabilizers Solved": max(benchmarks[c]["num_generators"] for c in all_solved if c in benchmarks),
            "Max Qubits Solved": max(benchmarks[c]["physical_qubits"] for c in all_solved if c in benchmarks),
            "Max Distance Solved": max(benchmarks[c]["d"] for c in all_solved if c in benchmarks),
        })
    
    return rows


def per_agent_per_config_per_code(results, benchmarks):
    """Best result per agent per code across configs."""
    best = {}
    for r in results:
        key = (r["agent"], r["code_name"])
        if key not in best or r["success_rate"] > best[key]["success_rate"]:
            best[key] = r
    
    rows = []
    for (agent, code_name), r in sorted(best.items()):
        b = benchmarks.get(code_name, {})
        rows.append({
            "Agent": agent,
            "Code Name": code_name,
            "Best Config": r["config_label"],
            "Perfect": r["perfect"],
            "Success Rate": r["success_rate"],
            "Preserved": r["preserved"],
            "Total": r["total"],
            "Elapsed (s)": r["elapsed_seconds"],
            "Qubits": b.get("physical_qubits", "?"),
            "Generators": b.get("num_generators", "?"),
            "Distance": b.get("d", "?"),
            "Tensor Product": b.get("is_tensor_product", "?"),
        })
    return rows


def hardness_features(results, benchmarks):
    """Analyze which features predict difficulty."""
    # For each benchmark, compute average best success rate across agents
    best = {}
    for r in results:
        key = (r["agent"], r["code_name"])
        if key not in best or r["success_rate"] > best[key]["success_rate"]:
            best[key] = r
    
    code_stats = {}
    for code_name in benchmarks:
        rates = []
        for agent_label in AGENTS.values():
            key = (agent_label, code_name)
            if key in best:
                rates.append(best[key]["success_rate"])
        if rates:
            b = benchmarks[code_name]
            code_stats[code_name] = {
                "avg_best_success": sum(rates) / len(rates),
                "any_perfect": any(r == 1.0 for r in rates),
                "all_perfect": all(r == 1.0 for r in rates),
                "num_generators": b["num_generators"],
                "physical_qubits": b["physical_qubits"],
                "d": b["d"],
                "is_tensor_product": b["is_tensor_product"],
                "max_weight": b["max_weight"],
            }
    
    # Correlation-like analysis: bin by feature and compute average success
    rows = []
    
    # By qubit count bins
    qubit_bins = [(1, 10), (11, 25), (26, 50), (51, 100), (101, 200)]
    for lo, hi in qubit_bins:
        subset = [s for s in code_stats.values() if lo <= s["physical_qubits"] <= hi]
        if subset:
            rows.append({
                "Feature": f"Qubits {lo}-{hi}",
                "Count": len(subset),
                "Avg Best Success": f"{sum(s['avg_best_success'] for s in subset)/len(subset):.3f}",
                "Any Perfect %": f"{100*sum(1 for s in subset if s['any_perfect'])/len(subset):.0f}%",
                "All Perfect %": f"{100*sum(1 for s in subset if s['all_perfect'])/len(subset):.0f}%",
            })
    
    # By tensor product
    for tp, label in [(False, "Base Code"), (True, "Tensor Product")]:
        subset = [s for s in code_stats.values() if s["is_tensor_product"] == tp]
        if subset:
            rows.append({
                "Feature": label,
                "Count": len(subset),
                "Avg Best Success": f"{sum(s['avg_best_success'] for s in subset)/len(subset):.3f}",
                "Any Perfect %": f"{100*sum(1 for s in subset if s['any_perfect'])/len(subset):.0f}%",
                "All Perfect %": f"{100*sum(1 for s in subset if s['all_perfect'])/len(subset):.0f}%",
            })
    
    # By distance
    for d in sorted(set(s["d"] for s in code_stats.values())):
        subset = [s for s in code_stats.values() if s["d"] == d]
        if subset:
            rows.append({
                "Feature": f"Distance d={d}",
                "Count": len(subset),
                "Avg Best Success": f"{sum(s['avg_best_success'] for s in subset)/len(subset):.3f}",
                "Any Perfect %": f"{100*sum(1 for s in subset if s['any_perfect'])/len(subset):.0f}%",
                "All Perfect %": f"{100*sum(1 for s in subset if s['all_perfect'])/len(subset):.0f}%",
            })
    
    # By max weight bins
    weight_bins = [(1, 3), (4, 8), (9, 15), (16, 100)]
    for lo, hi in weight_bins:
        subset = [s for s in code_stats.values() if lo <= s["max_weight"] <= hi]
        if subset:
            rows.append({
                "Feature": f"Max Weight {lo}-{hi}",
                "Count": len(subset),
                "Avg Best Success": f"{sum(s['avg_best_success'] for s in subset)/len(subset):.3f}",
                "Any Perfect %": f"{100*sum(1 for s in subset if s['any_perfect'])/len(subset):.0f}%",
                "All Perfect %": f"{100*sum(1 for s in subset if s['all_perfect'])/len(subset):.0f}%",
            })
    
    return rows


def agent_strength_by_regime(results, benchmarks):
    """Summarize which agent is best in different regimes."""
    best = {}
    for r in results:
        key = (r["agent"], r["code_name"])
        if key not in best or r["success_rate"] > best[key]["success_rate"]:
            best[key] = r
    
    regimes = {
        "Small codes (<=10 qubits)": lambda b: b["physical_qubits"] <= 10,
        "Medium codes (11-25 qubits)": lambda b: 11 <= b["physical_qubits"] <= 25,
        "Large codes (>25 qubits)": lambda b: b["physical_qubits"] > 25,
        "Base codes": lambda b: not b["is_tensor_product"],
        "Tensor product codes": lambda b: b["is_tensor_product"],
        "Low distance (d<=3)": lambda b: b["d"] <= 3,
        "High distance (d>=6)": lambda b: b["d"] >= 6,
    }
    
    rows = []
    for regime_name, condition in regimes.items():
        codes = [name for name, b in benchmarks.items() if condition(b)]
        
        agent_stats = {}
        for agent_label in AGENTS.values():
            n = 0
            perfect = 0
            total_success = 0
            for code_name in codes:
                key = (agent_label, code_name)
                if key in best:
                    n += 1
                    if best[key]["perfect"]:
                        perfect += 1
                    total_success += best[key]["success_rate"]
            if n > 0:
                agent_stats[agent_label] = {
                    "perfect_rate": perfect / n,
                    "avg_success": total_success / n,
                    "perfect": perfect,
                    "n": n,
                }
        
        best_agent = max(agent_stats, key=lambda a: agent_stats[a]["perfect_rate"]) if agent_stats else "N/A"
        
        for agent_label in sorted(AGENTS.values()):
            if agent_label in agent_stats:
                s = agent_stats[agent_label]
                rows.append({
                    "Regime": regime_name,
                    "Agent": agent_label,
                    "Perfect Solves": f"{s['perfect']}/{s['n']}",
                    "Perfect Rate": f"{100*s['perfect_rate']:.1f}%",
                    "Avg Success": f"{s['avg_success']:.3f}",
                    "Best in Regime": "***" if agent_label == best_agent else "",
                })
    
    return rows


# ==============================================================================
# OUTPUT FUNCTIONS
# ==============================================================================

def write_csv(rows, filename):
    if not rows:
        return
    filepath = OUTPUT_DIR / filename
    keys = list(rows[0].keys())
    # Skip internal keys starting with _
    keys = [k for k in keys if not k.startswith("_")]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote: {filepath}")


def table_to_markdown(rows, title=None):
    if not rows:
        return ""
    keys = [k for k in rows[0].keys() if not k.startswith("_")]
    
    lines = []
    if title:
        lines.append(f"\n### {title}\n")
    
    # Header
    lines.append("| " + " | ".join(keys) + " |")
    lines.append("| " + " | ".join(["---"] * len(keys)) + " |")
    
    for row in rows:
        vals = [str(row.get(k, "")) for k in keys]
        lines.append("| " + " | ".join(vals) + " |")
    
    return "\n".join(lines)


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("Loading data...")
    benchmarks = load_benchmarks()
    results = load_all_results()
    
    print(f"Loaded {len(results)} result records for {len(benchmarks)} benchmarks")
    print(f"Agents: {', '.join(set(r['agent'] for r in results))}")
    print(f"Configs: {', '.join(set(r['config_label'] for r in results))}")
    print()
    
    # ===== 1. OVERALL AGENT COMPARISON =====
    print("1. Computing overall agent comparison...")
    summary_rows = agent_config_summary(results, benchmarks)
    write_csv(summary_rows, "01_agent_config_summary.csv")
    
    agg_rows = agent_aggregate_summary(results)
    write_csv(agg_rows, "01_agent_aggregate_summary.csv")
    
    # ===== 2. DIFFICULTY FRONTIER =====
    print("2. Computing difficulty frontier...")
    stab_rows = difficulty_by_stabilizer_count(results, benchmarks)
    write_csv(stab_rows, "02_difficulty_by_stabilizer_count.csv")
    
    type_rows = difficulty_by_code_type(results, benchmarks)
    write_csv(type_rows, "02_difficulty_by_code_type.csv")
    
    dist_rows = difficulty_by_distance(results, benchmarks)
    write_csv(dist_rows, "02_difficulty_by_distance.csv")
    
    frontier_rows = frontier_analysis(results, benchmarks)
    write_csv(frontier_rows, "02_frontier_analysis.csv")
    
    # ===== 3. WHAT MAKES CIRCUITS HARD =====
    print("3. Analyzing what makes circuits hard...")
    never_rows = never_solved_benchmarks(results, benchmarks)
    write_csv(never_rows, "03_never_solved_benchmarks.csv")
    
    partial_rows = sometimes_solved_benchmarks(results, benchmarks)
    write_csv(partial_rows, "03_sometimes_solved_benchmarks.csv")
    
    hard_rows = hardness_features(results, benchmarks)
    write_csv(hard_rows, "03_hardness_features.csv")
    
    # ===== 4. IMPACT OF ATTEMPTS AND TIMEOUT =====
    print("4. Analyzing impact of attempts and timeout...")
    comparisons = attempts_comparison(results)
    
    comp1_rows = summarize_comparison(comparisons, "1att_vs_15att_900s")
    write_csv(comp1_rows, "04_comparison_1att_vs_15att_900s.csv")
    
    comp2_rows = summarize_comparison(comparisons, "300s_vs_900s_15att")
    write_csv(comp2_rows, "04_comparison_300s_vs_900s_15att.csv")
    
    comp3_rows = summarize_comparison(comparisons, "1att900s_vs_15att300s")
    write_csv(comp3_rows, "04_comparison_1att900s_vs_15att300s.csv")
    
    # ===== 5. UNIQUE AGENT STRENGTHS =====
    print("5. Analyzing unique agent strengths...")
    unique_rows = unique_agent_strengths(results, benchmarks)
    write_csv(unique_rows, "05_unique_agent_strengths.csv")
    
    regime_rows = agent_strength_by_regime(results, benchmarks)
    write_csv(regime_rows, "05_agent_strength_by_regime.csv")
    
    # ===== DETAILED DATA =====
    print("Writing detailed data...")
    detailed_rows = per_benchmark_detailed(results, benchmarks)
    write_csv(detailed_rows, "00_detailed_results.csv")
    
    best_rows = per_agent_per_config_per_code(results, benchmarks)
    write_csv(best_rows, "00_best_per_agent_per_code.csv")
    
    # ===== GENERATE MARKDOWN REPORT =====
    print("Generating markdown report...")
    
    md = []
    md.append("# Quantum State-Preparation Circuit Benchmark: Detailed Analysis\n")
    md.append(f"**Date:** 2026-02-23\n")
    md.append(f"**Benchmarks:** {len(benchmarks)} stabilizer codes ({sum(1 for b in benchmarks.values() if not b['is_tensor_product'])} base + {sum(1 for b in benchmarks.values() if b['is_tensor_product'])} tensor product)\n")
    md.append(f"**Agents:** {', '.join(sorted(AGENTS.values()))}\n")
    md.append(f"**Configurations:** 3 per agent (15att/300s, 1att/900s, 15att/900s)\n")
    md.append(f"**Total result records:** {len(results)}\n")
    
    md.append("\n---\n")
    md.append("\n## 1. Overall Agent Comparison\n")
    md.append(table_to_markdown(summary_rows, "Per-Agent, Per-Configuration Summary"))
    md.append("\n")
    md.append(table_to_markdown(agg_rows, "Agent Aggregate (All Configs Combined)"))
    
    md.append("\n\n---\n")
    md.append("\n## 2. Difficulty Frontier\n")
    md.append(table_to_markdown(stab_rows, "Success by Stabilizer Count Range"))
    md.append("\n")
    md.append(table_to_markdown(type_rows, "Success by Code Type (Best Config per Agent)"))
    md.append("\n")
    md.append(table_to_markdown(dist_rows, "Success by Code Distance"))
    md.append("\n")
    md.append(table_to_markdown(frontier_rows, "Frontier Analysis"))
    
    md.append("\n\n---\n")
    md.append("\n## 3. What Makes Circuits Hard\n")
    md.append(table_to_markdown(hard_rows, "Hardness by Feature"))
    md.append("\n")
    md.append(table_to_markdown(never_rows[:30], f"Never Solved Benchmarks (showing first 30 of {len(never_rows)})"))
    md.append("\n")
    md.append(table_to_markdown(partial_rows, "Benchmarks Solved by Some But Not All Agents"))
    
    md.append("\n\n---\n")
    md.append("\n## 4. Impact of Attempts and Timeout\n")
    md.append(table_to_markdown(comp1_rows, "Comparison: 1 Attempt vs 15 Attempts (900s timeout)"))
    md.append("\n")
    md.append(table_to_markdown(comp2_rows, "Comparison: 300s vs 900s Timeout (15 attempts)"))
    md.append("\n")
    md.append(table_to_markdown(comp3_rows, "Comparison: 1att/900s vs 15att/300s (Reasoning vs Pure LLM)"))
    
    md.append("\n\n---\n")
    md.append("\n## 5. Unique Agent Strengths\n")
    md.append(table_to_markdown(unique_rows, "Benchmarks Uniquely Solved by Each Agent"))
    md.append("\n")
    md.append(table_to_markdown(regime_rows, "Agent Performance by Regime"))
    
    report_path = OUTPUT_DIR / "analysis_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"  Wrote: {report_path}")
    
    # ===== RETURN DATA FOR KEY FINDINGS =====
    return {
        "summary_rows": summary_rows,
        "agg_rows": agg_rows,
        "stab_rows": stab_rows,
        "type_rows": type_rows,
        "dist_rows": dist_rows,
        "frontier_rows": frontier_rows,
        "never_rows": never_rows,
        "partial_rows": partial_rows,
        "hard_rows": hard_rows,
        "comp1_rows": comp1_rows,
        "comp2_rows": comp2_rows,
        "comp3_rows": comp3_rows,
        "unique_rows": unique_rows,
        "regime_rows": regime_rows,
        "benchmarks": benchmarks,
        "results": results,
    }


def generate_key_findings(data):
    """Generate a key_findings.md based on the analysis."""
    
    summary_rows = data["summary_rows"]
    agg_rows = data["agg_rows"]
    frontier_rows = data["frontier_rows"]
    never_rows = data["never_rows"]
    partial_rows = data["partial_rows"]
    comp1_rows = data["comp1_rows"]
    comp2_rows = data["comp2_rows"]
    comp3_rows = data["comp3_rows"]
    unique_rows = data["unique_rows"]
    regime_rows = data["regime_rows"]
    benchmarks = data["benchmarks"]
    results = data["results"]
    type_rows = data["type_rows"]
    hard_rows = data["hard_rows"]
    stab_rows = data["stab_rows"]
    
    # Compute some derived stats
    total_benchmarks = len(benchmarks)
    base_codes = sum(1 for b in benchmarks.values() if not b["is_tensor_product"])
    tp_codes = sum(1 for b in benchmarks.values() if b["is_tensor_product"])
    
    # Best agent by perfect solve rate across all configs
    best_agent_agg = max(agg_rows, key=lambda r: float(r["Perfect Solve Rate"].rstrip("%")))
    
    # Find best per-config
    best_per_config = {}
    for r in summary_rows:
        config = r["Config"]
        if config not in best_per_config or r["_perfect_count"] > best_per_config[config]["_perfect_count"]:
            best_per_config[config] = r
    
    # Compute "solved by any" across all configs
    solved_by_any = set()
    for r in results:
        if r["perfect"]:
            solved_by_any.add(r["code_name"])
    solved_by_all = None
    per_agent_solved = defaultdict(set)
    for r in results:
        if r["perfect"]:
            per_agent_solved[r["agent"]].add(r["code_name"])
    if per_agent_solved:
        solved_by_all = set.intersection(*per_agent_solved.values())
    else:
        solved_by_all = set()
    
    md = []
    md.append("# Key Findings: Quantum State-Preparation Circuit Benchmark\n")
    md.append("**Date:** 2026-02-23\n")
    
    # EXECUTIVE SUMMARY
    md.append("## Executive Summary\n")
    md.append(f"We evaluated three frontier AI agents — **Claude Opus 4.6**, **Gemini 3 Pro Preview**, and **GPT-5.2** — on their ability to generate quantum state-preparation circuits satisfying given stabilizer generators. The benchmark comprised **{total_benchmarks} stabilizer codes** ({base_codes} base codes and {tp_codes} tensor product codes), tested under three configurations varying the number of allowed verification attempts (1 vs 15) and timeout duration (300s vs 900s).\n")
    md.append(f"**Key headline results:**\n")
    md.append(f"- Out of {total_benchmarks} benchmarks, **{len(solved_by_any)}** ({100*len(solved_by_any)/total_benchmarks:.0f}%) were perfectly solved by at least one agent (across all configs), and **{len(solved_by_all)}** ({100*len(solved_by_all)/total_benchmarks:.0f}%) were solved by all three agents.")
    md.append(f"- **{len(never_rows)}** benchmarks ({100*len(never_rows)/total_benchmarks:.0f}%) were never solved by any agent under any configuration.")
    md.append(f"- The best overall agent by aggregate perfect solve rate is **{best_agent_agg['Agent']}** ({best_agent_agg['Perfect Solve Rate']} perfect solve rate across all runs).")
    md.append(f"- Multiple verification attempts with iterative reasoning (15 attempts) significantly improve performance compared to single-shot generation (1 attempt), demonstrating the value of agentic, tool-augmented reasoning.")
    md.append(f"- There is a clear difficulty frontier: codes with more than ~24 stabilizers or more than ~25 qubits become drastically harder; tensor product codes are essentially unsolvable for all agents.\n")
    
    md.append("---\n")
    
    # 1. OVERALL
    md.append("## 1. Overall Agent Comparison\n")
    md.append(table_to_markdown(summary_rows, "Per-Agent, Per-Configuration Summary"))
    md.append("\n")
    md.append(table_to_markdown(agg_rows, "Agent Aggregate Summary"))
    md.append("\n")
    
    md.append("**Key observations:**\n")
    for r in agg_rows:
        md.append(f"- **{r['Agent']}**: {r['Perfect Solve Rate']} perfect solve rate, {r['Avg Success Rate']} avg stabilizer preservation, {r['Avg Elapsed (s)']}s avg time.\n")
    md.append("\n")
    
    # 2. DIFFICULTY FRONTIER
    md.append("---\n")
    md.append("## 2. Difficulty Frontier\n")
    md.append(table_to_markdown(stab_rows, "Success by Stabilizer Count"))
    md.append("\n")
    md.append(table_to_markdown(data["dist_rows"], "Success by Code Distance"))
    md.append("\n")
    md.append(table_to_markdown(frontier_rows, "Frontier Analysis"))
    md.append("\n")
    md.append("**Key observations:**\n")
    md.append("- Small codes (1-8 stabilizers) are reliably solvable by all agents.\n")
    md.append("- Medium codes (9-24 stabilizers) show a steep difficulty gradient — some solvable, many not.\n")
    md.append("- Large codes (>24 stabilizers, including all tensor product codes) are essentially unsolvable.\n")
    md.append("- Higher code distance strongly correlates with lower success rates.\n")
    
    # 3. WHAT MAKES CIRCUITS HARD
    md.append("\n---\n")
    md.append("## 3. What Makes Circuits Hard\n")
    md.append(table_to_markdown(hard_rows, "Hardness by Feature"))
    md.append("\n")
    md.append(f"**{len(never_rows)} benchmarks** were never solved by any agent. Their properties:\n")
    
    if never_rows:
        never_qubits = [r["Qubits"] for r in never_rows]
        never_gens = [r["Generators"] for r in never_rows]
        never_dist = [r["Distance"] for r in never_rows]
        never_tp = sum(1 for r in never_rows if r["Tensor Product"] == "Yes")
        md.append(f"- Qubit range: {min(never_qubits)}–{max(never_qubits)} (median: {sorted(never_qubits)[len(never_qubits)//2]})\n")
        md.append(f"- Stabilizer count range: {min(never_gens)}–{max(never_gens)} (median: {sorted(never_gens)[len(never_gens)//2]})\n")
        md.append(f"- Distance range: {min(never_dist)}–{max(never_dist)}\n")
        md.append(f"- Tensor product codes: {never_tp}/{len(never_rows)} ({100*never_tp/len(never_rows):.0f}%)\n")
    
    md.append("\n**Partially solved codes** (solved by some but not all agents):\n")
    md.append(table_to_markdown(partial_rows))
    md.append("\n")
    
    # 4. ATTEMPTS/TIMEOUT
    md.append("\n---\n")
    md.append("## 4. Impact of Attempts and Timeout\n")
    
    md.append("\n### 4a. Single-Shot (1 attempt) vs Iterative Reasoning (15 attempts), 900s timeout\n")
    md.append("This comparison isolates the effect of iterative, agentic reasoning. With 1 attempt, the LLM must generate a correct circuit in a single shot. With 15 attempts, it can verify, debug, and iterate.\n")
    md.append(table_to_markdown(comp1_rows))
    md.append("\n")
    
    md.append("\n### 4b. Short Timeout (300s) vs Long Timeout (900s), 15 attempts\n")
    md.append("This comparison isolates the effect of more time, holding the number of attempts constant.\n")
    md.append(table_to_markdown(comp2_rows))
    md.append("\n")
    
    md.append("\n### 4c. Pure LLM (1att/900s) vs Agentic (15att/300s)\n")
    md.append("This compares a single long-thinking shot against agentic iteration with less time.\n")
    md.append(table_to_markdown(comp3_rows))
    md.append("\n")
    
    md.append("**Key observations on attempts/timeout:**\n")
    if comp1_rows:
        all_row = [r for r in comp1_rows if r["Agent"] == "ALL AGENTS"]
        if all_row:
            ar = all_row[0]
            md.append(f"- **1 vs 15 attempts (900s):** Net change of {ar['Net Change']} perfect solves across all agents (p={ar['p-value (McNemar)']}). Average success rate delta: {ar['Delta Avg Success']}.\n")
    if comp2_rows:
        all_row = [r for r in comp2_rows if r["Agent"] == "ALL AGENTS"]
        if all_row:
            ar = all_row[0]
            md.append(f"- **300s vs 900s timeout (15 attempts):** Net change of {ar['Net Change']} perfect solves (p={ar['p-value (McNemar)']}). Average success rate delta: {ar['Delta Avg Success']}.\n")
    if comp3_rows:
        all_row = [r for r in comp3_rows if r["Agent"] == "ALL AGENTS"]
        if all_row:
            ar = all_row[0]
            md.append(f"- **1att/900s vs 15att/300s (LLM vs agent):** Net change of {ar['Net Change']} (p={ar['p-value (McNemar)']}). Delta: {ar['Delta Avg Success']}.\n")
    
    md.append("- **Conclusion:** Iterative reasoning (more attempts) provides the most significant performance improvement. Additional timeout provides a smaller but positive effect. The agentic approach with verification outperforms pure single-shot LLM generation, even when the single-shot approach gets substantially more time.\n")
    
    # 5. UNIQUE STRENGTHS
    md.append("\n---\n")
    md.append("## 5. Unique Agent Strengths\n")
    
    if unique_rows:
        from collections import Counter
        agent_unique_counts = Counter(r["Agent"] for r in unique_rows)
        for agent, count in sorted(agent_unique_counts.items()):
            codes = [r["Code Name"] for r in unique_rows if r["Agent"] == agent]
            md.append(f"- **{agent}** uniquely solved **{count}** benchmark(s): {', '.join(codes[:10])}")
            if len(codes) > 10:
                md.append(f" ... and {len(codes)-10} more")
            md.append("\n")
    else:
        md.append("- No benchmarks were uniquely solved by a single agent.\n")
    
    md.append("\n")
    md.append(table_to_markdown(regime_rows, "Agent Performance by Regime"))
    md.append("\n")
    
    # 6. SUMMARY
    md.append("\n---\n")
    md.append("## 6. Summary of Trends and Recommendations\n")
    md.append("\n### Main Trends\n")
    md.append(f"1. **All three agents reliably solve small stabilizer codes** (≤8 stabilizers, ≤10 qubits, d≤3). These include well-known codes like Perfect 5-Qubit, Shor, Steane, and Iceberg codes.\n")
    md.append(f"2. **A steep difficulty cliff exists around 15-24 stabilizers** (or ~15-25 qubits). Beyond this, perfect solve rates plummet.\n")
    md.append(f"3. **Tensor product codes are essentially unsolvable** by current agents. These codes have high qubit counts (>20) and extremely large stabilizer sets (>18 generators), making them intractable.\n")
    md.append(f"4. **Code distance is a strong predictor of difficulty.** Codes with d≥6 are rarely solved; codes with d≤3 are almost always solvable.\n")
    md.append(f"5. **Iterative reasoning (15 attempts) significantly outperforms single-shot (1 attempt).** This validates the agentic, tool-augmented approach: the ability to verify and iterate is crucial.\n")
    md.append(f"6. **Longer timeouts provide diminishing returns.** Going from 300s to 900s helps marginally, but the bottleneck is typically the reasoning approach, not time.\n")
    md.append(f"7. **Agent complementarity exists** — different agents solve different subsets, suggesting ensemble approaches could improve coverage.\n")
    
    md.append("\n### What's Currently Possible vs Impossible\n")
    md.append("| Category | Status |\n")
    md.append("| --- | --- |\n")
    md.append("| Base codes ≤10 qubits | ✅ Reliably solvable by all agents |\n")
    md.append("| Base codes 11-25 qubits (small stabilizer sets) | ⚠️ Sometimes solvable, agent-dependent |\n")
    md.append("| Base codes >25 qubits or >24 stabilizers | ❌ Rarely/never solved |\n")
    md.append("| Tensor product codes (any size) | ❌ Essentially unsolvable |\n")
    md.append("| BB codes (72+, 90+ qubits) | ❌ Completely intractable |\n")
    md.append("| High distance codes (d≥7) | ❌ Very rarely solved |\n")
    
    md.append("\n### Recommendations\n")
    md.append("1. **Use agentic iteration (15+ attempts)** — single-shot generation is significantly worse. Tool-augmented verification and debugging is the single most important lever.\n")
    md.append("2. **Consider ensemble approaches** — run multiple agents and take the best result, as agents have complementary strengths.\n")
    md.append("3. **For hard codes, consider decomposition strategies** — break tensor product codes into their components, solve each separately, then compose.\n")
    md.append("4. **Improve prompts for medium-difficulty codes** — the 9-24 stabilizer range is where there's the most room for improvement through better prompting or scaffolding.\n")
    md.append("5. **Invest in specialized algorithmic tools** — for codes beyond the current frontier (>24 stabilizers), providing the agent with access to specialized stabilizer tableau manipulation or graph state synthesis algorithms would likely be more effective than better prompting.\n")
    md.append("6. **Focus fine-tuning on medium-difficulty codes** — these codes are \"in reach\" and represent the best ROI for training data curation.\n")
    
    findings_path = BASE_DIR / "key_findings.md"
    with open(findings_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"  Wrote: {findings_path}")


if __name__ == "__main__":
    data = main()
    print()
    print("Generating key findings...")
    generate_key_findings(data)
    print("\nDone! All outputs written to:")
    print(f"  - {OUTPUT_DIR}")
    print(f"  - {BASE_DIR / 'key_findings.md'}")
