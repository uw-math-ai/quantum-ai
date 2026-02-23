"""
Deep analysis of quantum state-preparation benchmark results.

Focuses on:
  - Solvability limits and frontiers (what's possible vs. not)
  - Impact of attempts (1 vs 15) with statistical tests
  - Code-family and structural predictors of difficulty
  - Per-agent strengths/weaknesses by code type
  - Trends across qubit count, distance, and stabilizer count
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict
import statistics
import math

DATA_DIR = Path(__file__).parent / "data"
BENCHMARKS_FILE = Path(__file__).parent.parent / "data" / "benchmarks.json"

AGENTS = ["claude-opus-4.6", "gemini-3-pro-preview", "gpt5.2"]
AGENT_SHORT = {"claude-opus-4.6": "Claude", "gemini-3-pro-preview": "Gemini", "gpt5.2": "GPT-5.2"}

# -- Loading --------------------------------------------------------------

def load_benchmarks():
    """Load benchmark definitions -> dict keyed by name."""
    with open(BENCHMARKS_FILE, encoding="utf-8") as f:
        benchmarks = json.load(f)
    return {b["name"]: b for b in benchmarks}


def load_results():
    """Load all result files -> dict[agent][config_key] = {code_name: result}."""
    data = {}
    for agent in AGENTS:
        data[agent] = {}
        agent_path = DATA_DIR / agent
        for f in sorted(agent_path.glob("2602*.json")):
            with open(f, encoding="utf-8") as fh:
                raw = json.load(fh)
            meta = raw["metadata"]
            key = (meta["attempts"], meta["timeout"])
            data[agent][key] = {r["code_name"]: r for r in raw["results"]}
    return data


def parse_tensor_product(name):
    """Parse '(A) * (B)' -> (A, B) or return None for base codes."""
    m = re.match(r"^\((.+?)\) \* \((.+?)\)$", name)
    if m:
        return m.group(1), m.group(2)
    return None


def get_code_family(name):
    """Extract the code family from a base code name."""
    # Strip distance/parameter suffixes
    for pattern in [r" d=\d+", r" n=\d+", r" m=\d+", r" l=\d+"]:
        name = re.sub(pattern, "", name)
    return name.strip()


def print_sep(char="=", w=120):
    print(char * w)

def print_hdr(title):
    print()
    print_sep()
    print(f"  {title}")
    print_sep()


# -- Statistical helpers --------------------------------------------------

def mcnemar_test(n_01, n_10):
    """McNemar's chi-squared test for paired binary outcomes.
    n_01 = cases where config A fails but config B succeeds.
    n_10 = cases where config A succeeds but config B fails.
    Returns (chi2, p_value_approx).
    """
    total = n_01 + n_10
    if total == 0:
        return 0.0, 1.0
    chi2 = (abs(n_01 - n_10) - 1) ** 2 / total  # with continuity correction
    # Approximate p-value from chi2(1) using survival function approximation
    # For chi2(1): p ~ erfc(sqrt(chi2/2)) 
    p = math.erfc(math.sqrt(chi2 / 2))
    return chi2, p


def sign_test(diffs):
    """Simple sign test: how many positive vs negative diffs?"""
    pos = sum(1 for d in diffs if d > 0)
    neg = sum(1 for d in diffs if d < 0)
    zero = sum(1 for d in diffs if d == 0)
    return pos, neg, zero


# -- Analysis sections ----------------------------------------------------

def section_code_metadata(benchmarks):
    """Print metadata summary for all base codes."""
    print_hdr("A. BENCHMARK CODE METADATA")
    
    base_codes = {name: b for name, b in benchmarks.items() if parse_tensor_product(name) is None}
    tp_codes = {name: b for name, b in benchmarks.items() if parse_tensor_product(name) is not None}
    
    print(f"\n  {len(base_codes)} base codes, {len(tp_codes)} tensor product codes = {len(benchmarks)} total\n")
    print(f"  {'Base Code':<35} {'Qubits':>7} {'k':>4} {'d':>4} {'Stabs':>7}")
    print(f"  {'-'*33}  {'-'*5}  {'-'*3}  {'-'*3}  {'-'*5}")
    
    for name in sorted(base_codes, key=lambda n: base_codes[n]["physical_qubits"]):
        b = base_codes[name]
        n_stab = len(b["generators"])
        print(f"  {name:<35} {b['physical_qubits']:>7} {b['logical_qubits']:>4} {b['d']:>4} {n_stab:>7}")
    
    print(f"\n  Tensor product code qubit ranges:")
    tp_qubits = [b["physical_qubits"] for b in tp_codes.values()]
    tp_stabs = [len(b["generators"]) for b in tp_codes.values()]
    print(f"    Physical qubits: {min(tp_qubits)} - {max(tp_qubits)}")
    print(f"    Stabilizer count: {min(tp_stabs)} - {max(tp_stabs)}")
    
    return base_codes, tp_codes


def section_solvability_by_qubits(benchmarks, results):
    """Analyze solvability as a function of physical qubit count."""
    print_hdr("B. SOLVABILITY BY PHYSICAL QUBIT COUNT")
    
    # Use best config (15, 900) for solvability analysis
    cfg = (15, 900)
    
    # Build qubit bins
    bins = [(1, 10), (11, 20), (21, 30), (31, 50), (51, 80), (81, 120), (121, 200), (201, 500)]
    
    print(f"\n  Config: attempts=15, timeout=900s\n")
    print(f"  {'Qubit range':<15} {'#Bench':>8}", end="")
    for a in AGENTS:
        print(f"  {AGENT_SHORT[a]+' perf':>12}", end="")
    print(f"  {'Any agent':>12}  {'All agents':>12}")
    print(f"  {'-'*13}  {'-'*6}", end="")
    for _ in AGENTS:
        print(f"  {'-'*10}", end="")
    print(f"  {'-'*10}  {'-'*10}")
    
    for lo, hi in bins:
        subset_names = [name for name, b in benchmarks.items() 
                       if lo <= b["physical_qubits"] <= hi]
        if not subset_names:
            continue
        
        n = len(subset_names)
        agent_perfect = {}
        for a in AGENTS:
            if cfg in results[a]:
                agent_perfect[a] = sum(1 for name in subset_names 
                                      if name in results[a][cfg] and results[a][cfg][name]["success_rate"] == 1.0)
        
        # Any agent solved
        any_solved = 0
        all_solved = 0
        for name in subset_names:
            solved_by = [a for a in AGENTS if cfg in results[a] and name in results[a][cfg] and results[a][cfg][name]["success_rate"] == 1.0]
            if len(solved_by) > 0:
                any_solved += 1
            if len(solved_by) == len(AGENTS):
                all_solved += 1
        
        print(f"  {lo:>3}-{hi:<4}       {n:>8}", end="")
        for a in AGENTS:
            perf = agent_perfect.get(a, 0)
            print(f"  {perf:>5}/{n:<5}", end="")
        print(f"  {any_solved:>5}/{n:<5}  {all_solved:>5}/{n:<5}")


def section_solvability_by_stabilizers(benchmarks, results):
    """Analyze solvability as a function of stabilizer count."""
    print_hdr("C. SOLVABILITY BY STABILIZER COUNT")
    
    cfg = (15, 900)
    
    bins = [(1, 5), (6, 10), (11, 20), (21, 40), (41, 60), (61, 100), (101, 150), (151, 200)]
    
    print(f"\n  Config: attempts=15, timeout=900s\n")
    print(f"  {'Stab range':<15} {'#Bench':>8}", end="")
    for a in AGENTS:
        print(f"  {AGENT_SHORT[a]+' perf':>12}", end="")
    print(f"  {'Any agent':>12}  {'All agents':>12}")
    print(f"  {'-'*13}  {'-'*6}", end="")
    for _ in AGENTS:
        print(f"  {'-'*10}", end="")
    print(f"  {'-'*10}  {'-'*10}")
    
    for lo, hi in bins:
        subset_names = [name for name, b in benchmarks.items()
                       if lo <= len(b["generators"]) <= hi]
        if not subset_names:
            continue
        
        n = len(subset_names)
        agent_perfect = {}
        for a in AGENTS:
            if cfg in results[a]:
                agent_perfect[a] = sum(1 for name in subset_names
                                      if name in results[a][cfg] and results[a][cfg][name]["success_rate"] == 1.0)
        
        any_solved = 0
        all_solved = 0
        for name in subset_names:
            solved_by = [a for a in AGENTS if cfg in results[a] and name in results[a][cfg] and results[a][cfg][name]["success_rate"] == 1.0]
            if len(solved_by) > 0:
                any_solved += 1
            if len(solved_by) == len(AGENTS):
                all_solved += 1
        
        print(f"  {lo:>3}-{hi:<4}       {n:>8}", end="")
        for a in AGENTS:
            perf = agent_perfect.get(a, 0)
            print(f"  {perf:>5}/{n:<5}", end="")
        print(f"  {any_solved:>5}/{n:<5}  {all_solved:>5}/{n:<5}")


def section_code_family_analysis(benchmarks, results):
    """Analyze solvability by code family (grouping tensor products by their components)."""
    print_hdr("D. SOLVABILITY BY CODE FAMILY")
    
    cfg = (15, 900)
    
    # Group benchmarks by their base code families
    # For tensor products, categorize by BOTH components
    family_benchmarks = defaultdict(list)
    
    for name, b in benchmarks.items():
        tp = parse_tensor_product(name)
        if tp is None:
            family = get_code_family(name)
            family_benchmarks[f"Base: {family}"].append(name)
        else:
            fam_a = get_code_family(tp[0])
            fam_b = get_code_family(tp[1])
            family_benchmarks[f"TP: {fam_a} x {fam_b}"].append(name)
    
    print(f"\n  Config: attempts=15, timeout=900s")
    print(f"\n  {'Code Family':<55} {'#':>4}", end="")
    for a in AGENTS:
        print(f"  {AGENT_SHORT[a]:>8}", end="")
    print(f"  {'Any':>6}  {'All':>6}")
    print(f"  {'-'*53}  {'-'*3}", end="")
    for _ in AGENTS:
        print(f"  {'-'*6}", end="")
    print(f"  {'-'*4}  {'-'*4}")
    
    # Sort by family name
    for family in sorted(family_benchmarks.keys()):
        names = family_benchmarks[family]
        n = len(names)
        
        agent_perf = {}
        for a in AGENTS:
            if cfg in results[a]:
                agent_perf[a] = sum(1 for name in names
                                   if name in results[a][cfg] and results[a][cfg][name]["success_rate"] == 1.0)
        
        any_s = sum(1 for name in names if any(
            cfg in results[a] and name in results[a][cfg] and results[a][cfg][name]["success_rate"] == 1.0
            for a in AGENTS))
        all_s = sum(1 for name in names if all(
            cfg in results[a] and name in results[a][cfg] and results[a][cfg][name]["success_rate"] == 1.0
            for a in AGENTS))
        
        short_fam = family[:53]
        print(f"  {short_fam:<55} {n:>4}", end="")
        for a in AGENTS:
            p = agent_perf.get(a, 0)
            print(f"  {p:>4}/{n}", end="")
        print(f"  {any_s:>3}/{n}  {all_s:>3}/{n}")


def section_base_vs_tensor(benchmarks, results):
    """Compare base code performance vs tensor product performance."""
    print_hdr("E. BASE CODES vs. TENSOR PRODUCTS")
    
    cfg = (15, 900)
    
    base_names = [n for n in benchmarks if parse_tensor_product(n) is None]
    tp_names = [n for n in benchmarks if parse_tensor_product(n) is not None]
    
    for label, names in [("Base codes", base_names), ("Tensor products", tp_names)]:
        print(f"\n  {label} ({len(names)} benchmarks):")
        print(f"    {'Agent':<25} {'Perfect':>10} {'Completed':>12} {'Avg SR':>10} {'Avg Time':>10}")
        print(f"    {'-'*23}  {'-'*8}  {'-'*10}  {'-'*8}  {'-'*8}")
        
        for a in AGENTS:
            if cfg not in results[a]:
                continue
            res_list = [results[a][cfg][n] for n in names if n in results[a][cfg]]
            n = len(res_list)
            perfect = sum(1 for r in res_list if r["success_rate"] == 1.0)
            completed = sum(1 for r in res_list if r["circuit"] is not None)
            avg_sr = statistics.mean([r["success_rate"] for r in res_list]) if res_list else 0
            avg_time = statistics.mean([r["elapsed_seconds"] for r in res_list]) if res_list else 0
            
            print(f"    {AGENT_SHORT[a]:<25} {perfect:>4}/{n:<4}  {completed:>4}/{n:<6}  {avg_sr:>8.1%}  {avg_time:>7.1f}s")


def section_attempts_comparison(benchmarks, results):
    """Statistical comparison: 1 attempt vs 15 attempts (both with 900s timeout)."""
    print_hdr("F. IMPACT OF ATTEMPTS: 1 vs 15 (timeout=900s)")
    
    cfg1 = (1, 900)
    cfg15 = (15, 900)
    
    for a in AGENTS:
        if cfg1 not in results[a] or cfg15 not in results[a]:
            print(f"\n  {AGENT_SHORT[a]}: Missing config data, skipping.")
            continue
        
        r1 = results[a][cfg1]
        r15 = results[a][cfg15]
        
        common_names = set(r1.keys()) & set(r15.keys())
        
        # Paired comparison
        improved = []   # benchmarks that went from imperfect to perfect
        regressed = []  # benchmarks that went from perfect to imperfect
        both_perfect = 0
        both_imperfect = 0
        
        sr_diffs = []  # success_rate difference (15att - 1att)
        time_diffs = []  # time difference
        
        for name in sorted(common_names):
            sr1 = r1[name]["success_rate"]
            sr15 = r15[name]["success_rate"]
            t1 = r1[name]["elapsed_seconds"]
            t15 = r15[name]["elapsed_seconds"]
            
            sr_diffs.append(sr15 - sr1)
            time_diffs.append(t15 - t1)
            
            p1 = (sr1 == 1.0)
            p15 = (sr15 == 1.0)
            
            if p1 and p15:
                both_perfect += 1
            elif not p1 and not p15:
                both_imperfect += 1
            elif not p1 and p15:
                improved.append(name)
            else:
                regressed.append(name)
        
        n = len(common_names)
        n_01 = len(improved)   # fail@1 -> pass@15
        n_10 = len(regressed)  # pass@1 -> fail@15
        
        chi2, p_val = mcnemar_test(n_01, n_10)
        pos, neg, zero = sign_test(sr_diffs)
        
        perf1 = both_perfect + len(regressed)
        perf15 = both_perfect + len(improved)
        
        print(f"\n  {AGENT_SHORT[a]} ({n} benchmarks):")
        print(f"    Perfect solves:  1 attempt = {perf1:>4} ({perf1/n:.1%})  |  15 attempts = {perf15:>4} ({perf15/n:.1%})")
        print(f"    Both perfect:    {both_perfect:>4}  |  Both imperfect: {both_imperfect:>4}")
        print(f"    Improved (1->15): {n_01:>4}  |  Regressed (15->1): {n_10:>4}")
        print(f"    McNemar's test:  X^2={chi2:.2f}, p={p_val:.4f}  {'*SIGNIFICANT*' if p_val < 0.05 else '(not significant)'}")
        print(f"    SR diff (15-1):  mean={statistics.mean(sr_diffs):+.3f}, median={statistics.median(sr_diffs):+.3f}")
        print(f"    Sign test:       {pos} positive, {neg} negative, {zero} zero")
        print(f"    Time diff (15-1): mean={statistics.mean(time_diffs):+.1f}s, median={statistics.median(time_diffs):+.1f}s")
        
        # Show the specific benchmarks that improved
        if improved:
            print(f"\n    Benchmarks that IMPROVED from imperfect->perfect with 15 attempts:")
            for name in improved[:20]:  # limit display
                b = benchmarks.get(name, {})
                nq = b.get("physical_qubits", "?")
                ns = len(b.get("generators", []))
                sr1_val = r1[name]["success_rate"]
                print(f"      {name[:60]:<62} ({nq}q, {ns} stab)  SR: {sr1_val:.0%} -> 100%")
            if len(improved) > 20:
                print(f"      ... and {len(improved) - 20} more")
        
        if regressed:
            print(f"\n    Benchmarks that REGRESSED from perfect->imperfect with 15 attempts:")
            for name in regressed[:20]:
                b = benchmarks.get(name, {})
                nq = b.get("physical_qubits", "?")
                ns = len(b.get("generators", []))
                sr15_val = r15[name]["success_rate"]
                print(f"      {name[:60]:<62} ({nq}q, {ns} stab)  SR: 100% -> {sr15_val:.0%}")
            if len(regressed) > 20:
                print(f"      ... and {len(regressed) - 20} more")


def section_timeout_impact(benchmarks, results):
    """Compare configs with same attempts but different timeouts: (15,300) vs (15,900)."""
    print_hdr("G. IMPACT OF TIMEOUT: 300s vs 900s (attempts=15)")
    
    cfg_short = (15, 300)
    cfg_long = (15, 900)
    
    for a in AGENTS:
        if cfg_short not in results[a] or cfg_long not in results[a]:
            print(f"\n  {AGENT_SHORT[a]}: Missing config data, skipping.")
            continue
        
        r_s = results[a][cfg_short]
        r_l = results[a][cfg_long]
        
        common_names = set(r_s.keys()) & set(r_l.keys())
        n = len(common_names)
        
        improved = []
        regressed = []
        both_perfect = 0
        both_imperfect = 0
        
        for name in sorted(common_names):
            p_s = r_s[name]["success_rate"] == 1.0
            p_l = r_l[name]["success_rate"] == 1.0
            
            if p_s and p_l:
                both_perfect += 1
            elif not p_s and not p_l:
                both_imperfect += 1
            elif not p_s and p_l:
                improved.append(name)
            else:
                regressed.append(name)
        
        n_01 = len(improved)
        n_10 = len(regressed)
        chi2, p_val = mcnemar_test(n_01, n_10)
        
        perf_s = both_perfect + n_10
        perf_l = both_perfect + n_01
        
        print(f"\n  {AGENT_SHORT[a]} ({n} benchmarks):")
        print(f"    Perfect solves:  300s = {perf_s:>4} ({perf_s/n:.1%})  |  900s = {perf_l:>4} ({perf_l/n:.1%})")
        print(f"    Improved (300->900s): {n_01:>4}  |  Regressed: {n_10:>4}")
        print(f"    McNemar's test:  X^2={chi2:.2f}, p={p_val:.4f}  {'*SIGNIFICANT*' if p_val < 0.05 else '(not significant)'}")


def section_solvability_frontier(benchmarks, results):
    """Identify the solvability frontier: what's the max complexity that can be reliably solved?"""
    print_hdr("H. SOLVABILITY FRONTIER")
    
    cfg = (15, 900)
    
    # For each benchmark, compute "solvability score" = how many agents solved it perfectly
    benchmark_scores = []
    for name, b in benchmarks.items():
        nq = b["physical_qubits"]
        ns = len(b["generators"])
        is_tp = parse_tensor_product(name) is not None
        
        agents_solved = 0
        best_sr = 0
        for a in AGENTS:
            if cfg in results[a] and name in results[a][cfg]:
                sr = results[a][cfg][name]["success_rate"]
                if sr == 1.0:
                    agents_solved += 1
                best_sr = max(best_sr, sr)
        
        benchmark_scores.append({
            "name": name,
            "qubits": nq,
            "stabs": ns,
            "is_tp": is_tp,
            "agents_solved": agents_solved,
            "best_sr": best_sr,
        })
    
    # Sort by stabilizer count
    benchmark_scores.sort(key=lambda x: x["stabs"])
    
    # Find the frontier: largest stabilizer count where ALL agents solve it
    max_all_solved = 0
    max_any_solved = 0
    for bs in benchmark_scores:
        if bs["agents_solved"] == len(AGENTS):
            max_all_solved = max(max_all_solved, bs["stabs"])
        if bs["agents_solved"] > 0:
            max_any_solved = max(max_any_solved, bs["stabs"])
    
    print(f"\n  Frontier summary (config: attempts=15, timeout=900s):")
    print(f"    Max stabilizer count solved by ALL agents: {max_all_solved}")
    print(f"    Max stabilizer count solved by ANY agent:  {max_any_solved}")

    # Detailed: for each stabilizer count, show solve rate
    stab_groups = defaultdict(list)
    for bs in benchmark_scores:
        stab_groups[bs["stabs"]].append(bs)
    
    print(f"\n  {'Stabs':>6} {'#Bench':>7} {'All solve':>10} {'Any solve':>10} {'None solve':>11} {'Avg best SR':>12}")
    print(f"  {'-'*4}  {'-'*5}  {'-'*8}  {'-'*8}  {'-'*9}  {'-'*10}")
    
    for ns in sorted(stab_groups.keys()):
        group = stab_groups[ns]
        n = len(group)
        all_s = sum(1 for g in group if g["agents_solved"] == len(AGENTS))
        any_s = sum(1 for g in group if g["agents_solved"] > 0)
        none_s = sum(1 for g in group if g["agents_solved"] == 0)
        avg_best = statistics.mean([g["best_sr"] for g in group])
        
        print(f"  {ns:>6} {n:>7} {all_s:>5}/{n:<4} {any_s:>5}/{n:<4} {none_s:>5}/{n:<5} {avg_best:>10.1%}")


def section_universally_unsolved(benchmarks, results):
    """List benchmarks that NO agent can solve in any configuration."""
    print_hdr("I. UNIVERSALLY UNSOLVED BENCHMARKS")
    
    never_solved = []
    for name, b in benchmarks.items():
        solved_anywhere = False
        best_sr = 0
        best_detail = {}
        
        for a in AGENTS:
            for cfg_key, cfg_results in results[a].items():
                if name in cfg_results:
                    sr = cfg_results[name]["success_rate"]
                    if sr == 1.0:
                        solved_anywhere = True
                        break
                    if sr > best_sr:
                        best_sr = sr
                        best_detail = {
                            "agent": AGENT_SHORT[a],
                            "config": f"att={cfg_key[0]},to={cfg_key[1]}",
                            "preserved": cfg_results[name]["preserved"],
                            "total": cfg_results[name]["total"],
                        }
            if solved_anywhere:
                break
        
        if not solved_anywhere:
            nq = b["physical_qubits"]
            ns = len(b["generators"])
            never_solved.append({
                "name": name,
                "qubits": nq,
                "stabs": ns,
                "best_sr": best_sr,
                "best_detail": best_detail,
            })
    
    never_solved.sort(key=lambda x: x["stabs"])
    
    print(f"\n  {len(never_solved)} benchmarks never solved perfectly by any agent in any config:\n")
    if never_solved:
        print(f"  {'Benchmark':<62} {'Qubits':>7} {'Stabs':>6} {'Best SR':>8} {'By':>8}")
        print(f"  {'-'*60}  {'-'*5}  {'-'*4}  {'-'*6}  {'-'*6}")
        for ns in never_solved:
            d = ns["best_detail"]
            by_str = d.get("agent", "N/A")
            print(f"  {ns['name'][:60]:<62} {ns['qubits']:>7} {ns['stabs']:>6} {ns['best_sr']:>7.0%}  {by_str:>7}")
    
    # Analyze patterns
    if never_solved:
        print(f"\n  Pattern analysis of unsolved benchmarks:")
        tp_count = sum(1 for ns in never_solved if parse_tensor_product(ns["name"]) is not None)
        base_count = len(never_solved) - tp_count
        print(f"    Tensor products: {tp_count}  |  Base codes: {base_count}")
        
        qubit_vals = [ns["qubits"] for ns in never_solved]
        stab_vals = [ns["stabs"] for ns in never_solved]
        print(f"    Qubit range: {min(qubit_vals)} - {max(qubit_vals)}")
        print(f"    Stabilizer range: {min(stab_vals)} - {max(stab_vals)}")
        
        # Which code families appear most?
        family_count = defaultdict(int)
        for ns in never_solved:
            tp = parse_tensor_product(ns["name"])
            if tp:
                fam_a = get_code_family(tp[0])
                fam_b = get_code_family(tp[1])
                family_count[fam_a] += 1
                family_count[fam_b] += 1
        
        print(f"\n    Code families most represented in unsolved (as TP components):")
        for fam, count in sorted(family_count.items(), key=lambda x: -x[1]):
            print(f"      {fam:<40} appears {count:>3} times")


def section_uniquely_solved(benchmarks, results):
    """Identify benchmarks that only ONE agent can solve (unique strengths)."""
    print_hdr("J. UNIQUE AGENT STRENGTHS (benchmarks solved by exactly one agent)")
    
    cfg = (15, 900)
    
    for a in AGENTS:
        unique = []
        if cfg not in results[a]:
            continue
        
        for name, b in benchmarks.items():
            if name not in results[a][cfg]:
                continue
            if results[a][cfg][name]["success_rate"] != 1.0:
                continue
            
            # Check that no other agent solved it
            solved_by_other = False
            for other_a in AGENTS:
                if other_a == a:
                    continue
                if cfg in results[other_a] and name in results[other_a][cfg]:
                    if results[other_a][cfg][name]["success_rate"] == 1.0:
                        solved_by_other = True
                        break
            
            if not solved_by_other:
                nq = b["physical_qubits"]
                ns = len(b["generators"])
                unique.append({"name": name, "qubits": nq, "stabs": ns})
        
        unique.sort(key=lambda x: -x["stabs"])
        print(f"\n  {AGENT_SHORT[a]}: {len(unique)} uniquely solved benchmarks")
        if unique:
            for u in unique[:15]:
                print(f"    {u['name'][:65]:<67}  ({u['qubits']}q, {u['stabs']} stab)")
            if len(unique) > 15:
                print(f"    ... and {len(unique) - 15} more")


def section_distance_analysis(benchmarks, results):
    """Analyze solvability by code distance."""
    print_hdr("K. SOLVABILITY BY CODE DISTANCE")
    
    cfg = (15, 900)
    
    dist_groups = defaultdict(list)
    for name, b in benchmarks.items():
        d = b.get("d", None)
        if d is not None:
            dist_groups[d].append(name)
    
    print(f"\n  Config: attempts=15, timeout=900s\n")
    print(f"  {'Distance':>10} {'#Bench':>8}", end="")
    for a in AGENTS:
        print(f"  {AGENT_SHORT[a]:>10}", end="")
    print(f"  {'Any':>8}  {'None':>8}")
    print(f"  {'-'*8}  {'-'*6}", end="")
    for _ in AGENTS:
        print(f"  {'-'*8}", end="")
    print(f"  {'-'*6}  {'-'*6}")
    
    for d in sorted(dist_groups.keys()):
        names = dist_groups[d]
        n = len(names)
        
        agent_perf = {}
        for a in AGENTS:
            if cfg in results[a]:
                agent_perf[a] = sum(1 for name in names
                                   if name in results[a][cfg] and results[a][cfg][name]["success_rate"] == 1.0)
        
        any_s = sum(1 for name in names if any(
            cfg in results[a] and name in results[a][cfg] and results[a][cfg][name]["success_rate"] == 1.0
            for a in AGENTS))
        none_s = n - any_s
        
        print(f"  {d:>10} {n:>8}", end="")
        for a in AGENTS:
            p = agent_perf.get(a, 0)
            print(f"  {p:>4}/{n:<4}", end="")
        print(f"  {any_s:>4}/{n:<3}  {none_s:>4}/{n:<3}")


def section_tp_component_difficulty(benchmarks, results):
    """Analyze which tensor product COMPONENTS make benchmarks harder."""
    print_hdr("L. TENSOR PRODUCT COMPONENT DIFFICULTY")
    
    cfg = (15, 900)
    
    # For each base code, compute: when it appears as a TP component, what's the average solve rate?
    component_stats = defaultdict(lambda: {"total": 0, "solved_any": 0, "solved_all": 0, "sr_sum": 0})
    
    for name, b in benchmarks.items():
        tp = parse_tensor_product(name)
        if tp is None:
            continue
        
        agents_solved = 0
        best_sr = 0
        for a in AGENTS:
            if cfg in results[a] and name in results[a][cfg]:
                sr = results[a][cfg][name]["success_rate"]
                if sr == 1.0:
                    agents_solved += 1
                best_sr = max(best_sr, sr)
        
        for component in tp:
            fam = component  # use exact component name, not family
            component_stats[fam]["total"] += 1
            component_stats[fam]["sr_sum"] += best_sr
            if agents_solved > 0:
                component_stats[fam]["solved_any"] += 1
            if agents_solved == len(AGENTS):
                component_stats[fam]["solved_all"] += 1
    
    print(f"\n  Config: attempts=15, timeout=900s")
    print(f"  How solvable are tensor products containing each base code?\n")
    
    # Sort by solve rate
    components = sorted(component_stats.items(), 
                       key=lambda x: x[1]["solved_any"] / x[1]["total"] if x[1]["total"] > 0 else 0,
                       reverse=True)
    
    print(f"  {'Component':<40} {'# TPs':>6} {'Any solve':>10} {'All solve':>10} {'Avg best SR':>12}")
    print(f"  {'-'*38}  {'-'*4}  {'-'*8}  {'-'*8}  {'-'*10}")
    
    for comp, stats in components:
        n = stats["total"]
        avg_sr = stats["sr_sum"] / n if n > 0 else 0
        print(f"  {comp[:38]:<40} {n:>6} {stats['solved_any']:>5}/{n:<4} {stats['solved_all']:>5}/{n:<4} {avg_sr:>10.1%}")


def section_partial_solve_analysis(benchmarks, results):
    """Analyze benchmarks with partial success (0 < SR < 1): how close do agents get?"""
    print_hdr("M. PARTIAL SOLVE ANALYSIS")
    
    cfg = (15, 900)
    
    for a in AGENTS:
        if cfg not in results[a]:
            continue
        
        partial = []
        for name in sorted(results[a][cfg].keys()):
            r = results[a][cfg][name]
            sr = r["success_rate"]
            if 0 < sr < 1:
                b = benchmarks.get(name, {})
                partial.append({
                    "name": name,
                    "sr": sr,
                    "preserved": r["preserved"],
                    "total": r["total"],
                    "qubits": b.get("physical_qubits", "?"),
                    "stabs": len(b.get("generators", [])),
                })
        
        partial.sort(key=lambda x: -x["sr"])
        
        print(f"\n  {AGENT_SHORT[a]}: {len(partial)} benchmarks with partial success")
        if partial:
            print(f"    SR distribution: ", end="")
            for threshold in [0.9, 0.8, 0.5, 0.2]:
                count = sum(1 for p in partial if p["sr"] >= threshold)
                print(f">={threshold:.0%}: {count}  ", end="")
            print()
            
            # Show top near-misses (highest SR that isn't 100%)
            print(f"\n    Top near-misses (closest to perfect):")
            for p in partial[:10]:
                print(f"      {p['name'][:55]:<57}  {p['preserved']}/{p['total']} = {p['sr']:.1%}  ({p['qubits']}q, {p['stabs']} stab)")


def section_attempt_benefit_by_difficulty(benchmarks, results):
    """Does having more attempts help more for harder benchmarks?"""
    print_hdr("N. DO MORE ATTEMPTS HELP MORE FOR HARDER BENCHMARKS?")
    
    cfg1 = (1, 900)
    cfg15 = (15, 900)
    
    # Bin by stabilizer count, then see improvement from 1->15 attempts
    bins = [(1, 10), (11, 30), (31, 60), (61, 100), (101, 200)]
    
    print(f"\n  Comparing attempts=1 vs attempts=15 (both timeout=900s)")
    print(f"  Improvement = benchmarks that go from imperfect->perfect\n")
    
    for a in AGENTS:
        if cfg1 not in results[a] or cfg15 not in results[a]:
            continue
        
        r1 = results[a][cfg1]
        r15 = results[a][cfg15]
        
        print(f"  {AGENT_SHORT[a]}:")
        print(f"  {'Stab range':<15} {'#Bench':>7} {'Perf@1':>8} {'Perf@15':>9} {'Improved':>10} {'Regressed':>11} {'Net':>6}")
        print(f"  {'-'*13}  {'-'*5}  {'-'*6}  {'-'*7}  {'-'*8}  {'-'*9}  {'-'*4}")
        
        for lo, hi in bins:
            names = [n for n, b in benchmarks.items() 
                    if lo <= len(b.get("generators", [])) <= hi]
            
            perf1 = 0
            perf15 = 0
            improved = 0
            regressed = 0
            n = 0
            
            for name in names:
                if name not in r1 or name not in r15:
                    continue
                n += 1
                p1 = r1[name]["success_rate"] == 1.0
                p15 = r15[name]["success_rate"] == 1.0
                if p1:
                    perf1 += 1
                if p15:
                    perf15 += 1
                if not p1 and p15:
                    improved += 1
                if p1 and not p15:
                    regressed += 1
            
            if n > 0:
                net = improved - regressed
                net_str = f"+{net}" if net >= 0 else f"{net}"
                print(f"  {lo:>3}-{hi:<4}       {n:>7} {perf1:>5}/{n} {perf15:>6}/{n} {improved:>10} {regressed:>11} {net_str:>6}")
        
        print()


# -- Main -----------------------------------------------------------------

def main():
    print("\n" + "=" * 120)
    print("  DEEP ANALYSIS: QUANTUM STATE-PREPARATION CIRCUIT GENERATION")
    print("  Agents: " + ", ".join(AGENT_SHORT.values()))
    print("=" * 120)
    
    benchmarks = load_benchmarks()
    results = load_results()
    
    base_codes, tp_codes = section_code_metadata(benchmarks)
    section_solvability_by_qubits(benchmarks, results)
    section_solvability_by_stabilizers(benchmarks, results)
    section_code_family_analysis(benchmarks, results)
    section_base_vs_tensor(benchmarks, results)
    section_distance_analysis(benchmarks, results)
    section_tp_component_difficulty(benchmarks, results)
    section_attempts_comparison(benchmarks, results)
    section_timeout_impact(benchmarks, results)
    section_attempt_benefit_by_difficulty(benchmarks, results)
    section_solvability_frontier(benchmarks, results)
    section_universally_unsolved(benchmarks, results)
    section_uniquely_solved(benchmarks, results)
    section_partial_solve_analysis(benchmarks, results)
    
    print_hdr("END OF DEEP ANALYSIS")
    print()


if __name__ == "__main__":
    main()
