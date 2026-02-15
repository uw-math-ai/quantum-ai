"""
Evaluate a trained StepBasedCircuitAgent on specific stabilizer codes.

Usage:
    python reinforcement_learning/evaluation/evaluate_agent.py \
    --checkpoint reinforcement_learning/checkpoints/step_agent_ppo.pt \
    --num_qubits 20 --max_steps 64 --num_trials 5 --hidden_size 1024
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import torch

# Add project paths
ROOT_DIR = Path(__file__).resolve().parents[1] if "reinforcement_learning" in str(Path(__file__)) else Path(__file__).resolve().parent
RL_DIR = ROOT_DIR if ROOT_DIR.name == "reinforcement_learning" else ROOT_DIR / "reinforcement_learning"

sys.path.insert(0, str(RL_DIR / "agents"))
sys.path.insert(0, str(RL_DIR / "envs"))

# Try to find RL/envs for CircuitBuilderEnv
for candidate in [ROOT_DIR.parent / "RL" / "envs", ROOT_DIR / "RL" / "envs"]:
    if candidate.exists():
        sys.path.insert(0, str(candidate))
        break

from step_agent import StepBasedCircuitAgent
from CircuitBuilderEnv import CircuitBuilderEnv, CircuitBuilderConfig

# Add tools path for check_stabilizers
for candidate in [ROOT_DIR.parent / "tools", ROOT_DIR / "tools"]:
    if candidate.exists():
        sys.path.insert(0, str(candidate))
        break

from check_stabilizers import check_stabilizers


# ---- Built-in test codes ----
TEST_CODES = [
    {
        "name": "Perfect 5-Qubit Code",
        "physical_qubits": 5,
        "generators": ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"],
    },
    {
        "name": "Steane Code",
        "physical_qubits": 7,
        "generators": ["XXIIXXI", "XIXIXIX", "IIIXXXX", "ZZIIZZI", "ZIZIZIZ", "IIIZZZZ"],
    },
    {
        "name": "Shor Code",
        "physical_qubits": 9,
        "generators": [
            "XXXXXXIII", "XXXIIIXXX", "ZZIIIIIII", "ZIZIIIIII",
            "IIIZZIIII", "IIIZIZIII", "IIIIIIZZI", "IIIIIIZIZ",
        ],
    },
    {
        "name": "Iceberg m=2",
        "physical_qubits": 4,
        "generators": ["XXXX", "ZZZZ"],
    },
    {
        "name": "Iceberg m=3",
        "physical_qubits": 6,
        "generators": ["XXXXXX", "ZZZZZZ"],
    },
    {
        "name": "Hex Color Code d=3",
        "physical_qubits": 7,
        "generators": ["XXXXIII", "XIXIXIX", "IIXXXXI", "ZZZZIII", "ZIZIZIZ", "IIZZZZI"],
    },
    {
        "name": "Rotated Surface Code d=3",
        "physical_qubits": 9,
        "generators": [
            "XXIXXIIII", "IIIIXXIXX", "IIXIIXIII", "IIIXIIXII",
            "IIIZZIZZI", "IZZIZZIII", "ZZIIIIIII", "IIIIIIIZZ",
        ],
    },
    {
        "name": "Carbon Code",
        "physical_qubits": 12,
        "generators": [
            "XXXIIIXXXIII", "IIXXXIIIXXXI", "XIIIXXXIIIXX",
            "XXXXXXIIIIII", "IIIIIIXXXXXX", "IIZZZZIZIZII",
            "ZIIIZIZZZIIZ", "ZZZIIZZIIIZI", "ZIIZZZIIZIZI",
            "IZZIIIZZIZIZ",
        ],
    },
]


def load_agent(
    checkpoint_path: str,
    obs_shape: tuple,
    action_space_n: int,
    hidden_size: int = 512,
) -> StepBasedCircuitAgent:
    """Load a trained agent from checkpoint."""
    agent = StepBasedCircuitAgent(
        observation_shape=obs_shape,
        action_space_n=action_space_n,
        hidden_size=hidden_size,
    )
    state_dict = torch.load(checkpoint_path, map_location=agent.device, weights_only=True)
    agent.load_state_dict(state_dict)
    agent.eval()
    return agent


def evaluate_on_code(
    agent: StepBasedCircuitAgent,
    code: Dict[str, Any],
    num_qubits: int,
    max_steps: int,
    num_trials: int = 5,
    deterministic: bool = False,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Run the agent on a specific stabilizer code and report results."""
    generators = code["generators"]
    padded = [g.ljust(num_qubits, "I") for g in generators]

    config = CircuitBuilderConfig(max_gates=max_steps, num_qubits=num_qubits)
    
    results = []
    
    for trial in range(num_trials):
        env = CircuitBuilderEnv(padded, config=config, render_mode="string")
        obs = env.reset()
        
        done = False
        actions_taken = []
        step_count = 0
        
        while not done and step_count < max_steps:
            with torch.no_grad():
                if deterministic:
                    # Greedy: pick highest probability action
                    logits_list, _ = agent.forward(obs)
                    action = logits_list[0].argmax(dim=-1).item()
                else:
                    action, _, _ = agent.act(obs)
            
            obs, reward, done, _, info = env.step(action)
            action_decoded = env.int_to_action(action)
            actions_taken.append(action_decoded)
            step_count += 1
        
        # Check final stabilizer satisfaction
        circuit_str = str(env.circ)
        try:
            stab_results = check_stabilizers(circuit_str, generators)
            satisfied = sum(stab_results.values())
            total = len(generators)
        except Exception as e:
            satisfied = 0
            total = len(generators)
            stab_results = {g: False for g in generators}
        
        results.append({
            "trial": trial,
            "satisfied": satisfied,
            "total": total,
            "steps": step_count,
            "done": done,
            "stab_results": stab_results,
            "circuit": circuit_str,
            "actions": actions_taken,
        })
    
    # Summarize
    satisfactions = [r["satisfied"] for r in results]
    totals = results[0]["total"]
    best_trial = max(results, key=lambda r: (r["satisfied"], -r["steps"]))
    
    summary = {
        "code_name": code["name"],
        "physical_qubits": code["physical_qubits"],
        "num_stabilizers": totals,
        "best_satisfied": max(satisfactions),
        "avg_satisfied": sum(satisfactions) / len(satisfactions),
        "best_ratio": max(satisfactions) / totals,
        "avg_ratio": sum(satisfactions) / (len(satisfactions) * totals),
        "fully_solved_count": sum(1 for s in satisfactions if s == totals),
        "num_trials": num_trials,
        "best_steps": best_trial["steps"],
        "trials": results,
    }
    
    if verbose:
        solved_str = "✓" if summary["fully_solved_count"] > 0 else "✗"
        print(f"\n{'='*60}")
        print(f" {solved_str} {code['name']} ({code['physical_qubits']} qubits, {totals} stabilizers)")
        print(f"{'='*60}")
        print(f"  Best: {max(satisfactions)}/{totals} satisfied in {best_trial['steps']} gates")
        print(f"  Avg:  {summary['avg_satisfied']:.1f}/{totals} across {num_trials} trials")
        print(f"  Fully solved: {summary['fully_solved_count']}/{num_trials} trials")
        
        # Show per-stabilizer results for best trial
        print(f"\n  Stabilizer results (best trial):")
        for stab, result in best_trial["stab_results"].items():
            status = "✓" if result else "✗"
            print(f"    {status} {stab}")
        
        # Show first few actions of best trial
        if best_trial["actions"]:
            print(f"\n  First 10 actions:")
            for i, action in enumerate(best_trial["actions"][:10]):
                if len(action) == 2 and action[0] == "M":
                    print(f"    {i+1}. MEASURE k={action[1]}")
                elif len(action) == 2:
                    print(f"    {i+1}. {action[0]} q{action[1]}")
                else:
                    print(f"    {i+1}. {action[0]} q{action[1]} q{action[2]}")
            if len(best_trial["actions"]) > 10:
                print(f"    ... ({len(best_trial['actions'])} total)")
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Evaluate trained circuit-building agent")
    parser.add_argument(
        "--checkpoint", type=str,
        default="reinforcement_learning/checkpoints/step_agent_ppo.pt",
        help="Path to model checkpoint",
    )
    parser.add_argument("--num_qubits", type=int, default=20)
    parser.add_argument("--max_steps", type=int, default=64)
    parser.add_argument("--hidden_size", type=int, default=512)
    parser.add_argument("--num_trials", type=int, default=5,
                        help="Number of trials per code (agent is stochastic)")
    parser.add_argument("--deterministic", action="store_true",
                        help="Use greedy action selection instead of sampling")
    parser.add_argument("--code", type=str, default=None,
                        help="Evaluate only this code (by name)")
    parser.add_argument("--benchmarks", type=str, default=None,
                        help="Path to benchmarks JSON to test on those codes instead")
    parser.add_argument("--quiet", action="store_true",
                        help="Only print summary table")
    args = parser.parse_args()

    # Determine observation and action space from config
    config = CircuitBuilderConfig(max_gates=args.max_steps, num_qubits=args.num_qubits)
    obs_shape = (2 * args.num_qubits, 2 * args.num_qubits + 1)
    dummy_env = CircuitBuilderEnv(
        ["I" * args.num_qubits], config=config
    )
    action_space_n = dummy_env.action_space.n

    print(f"Loading checkpoint: {args.checkpoint}")
    print(f"Config: {args.num_qubits} qubits, {args.max_steps} max steps, {action_space_n} actions")
    print(f"Mode: {'deterministic' if args.deterministic else 'stochastic'} ({args.num_trials} trials)")

    agent = load_agent(
        args.checkpoint, obs_shape, action_space_n, args.hidden_size
    )
    print(f"Model loaded successfully\n")

    # Select codes to evaluate
    if args.benchmarks:
        with open(args.benchmarks) as f:
            codes = json.load(f)
    else:
        codes = TEST_CODES

    if args.code:
        codes = [c for c in codes if c["name"].lower() == args.code.lower()]
        if not codes:
            print(f"Code '{args.code}' not found. Available codes:")
            for c in TEST_CODES:
                print(f"  - {c['name']}")
            return

    # Filter to codes that fit num_qubits
    codes = [c for c in codes if c["physical_qubits"] <= args.num_qubits]

    # Run evaluation
    all_summaries = []
    for code in codes:
        summary = evaluate_on_code(
            agent, code, args.num_qubits, args.max_steps,
            num_trials=args.num_trials,
            deterministic=args.deterministic,
            verbose=not args.quiet,
        )
        all_summaries.append(summary)

    # Print summary table
    print(f"\n{'='*70}")
    print(f" SUMMARY")
    print(f"{'='*70}")
    print(f" {'Code':<30} {'Qubits':>6} {'Stabs':>6} {'Best':>8} {'Avg':>8} {'Solved':>8}")
    print(f" {'-'*30} {'-'*6} {'-'*6} {'-'*8} {'-'*8} {'-'*8}")
    
    total_solved = 0
    total_codes = len(all_summaries)
    
    for s in all_summaries:
        solved_str = f"{s['fully_solved_count']}/{s['num_trials']}"
        print(
            f" {s['code_name']:<30} {s['physical_qubits']:>6} "
            f"{s['num_stabilizers']:>6} "
            f"{s['best_satisfied']:>5}/{s['num_stabilizers']:>2} "
            f"{s['avg_satisfied']:>7.1f} "
            f"{solved_str:>8}"
        )
        if s['fully_solved_count'] > 0:
            total_solved += 1
    
    print(f"\n Codes with at least 1 solve: {total_solved}/{total_codes}")
    avg_ratio = sum(s['avg_ratio'] for s in all_summaries) / len(all_summaries)
    print(f" Average satisfaction ratio: {avg_ratio:.1%}")


if __name__ == "__main__":
    main()