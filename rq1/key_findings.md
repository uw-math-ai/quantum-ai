# Key Findings: Quantum State-Preparation Circuit Benchmark

**Date:** 2026-02-23

## Executive Summary

We evaluated three frontier AI agents — **Claude Opus 4.6**, **Gemini 3 Pro Preview**, and **GPT-5.2** — on their ability to generate quantum state-preparation circuits satisfying given stabilizer generators. The benchmark comprised **192 stabilizer codes** (24 base codes and 168 tensor product codes), tested under three configurations varying the number of allowed verification attempts (1 vs 15) and timeout duration (300s vs 900s).

**Key headline results:**

- Out of 192 benchmarks, **178** (93%) were perfectly solved by at least one agent (across all configs), and **138** (72%) were solved by all three agents.
- Only **14** benchmarks (7%) were never solved by any agent — all are very large tensor product codes (148–196 qubits, 146–194 stabilizers).
- The agents are remarkably close in overall performance: **Claude Opus 4.6** (59.2%), **GPT-5.2** (58.5%), and **Gemini 3 Pro Preview** (57.1%) aggregate perfect solve rates.
- **The most surprising finding: single-shot generation (1 attempt, 900s) outperforms iterative agentic reasoning (15 attempts, 900s)** by a significant margin (77.4% vs 69.4% perfect solve rate, p=0.0001). Extended thinking time for a single carefully-reasoned attempt beats trial-and-error iteration.
- **Timeout is the dominant factor**, not number of attempts. Going from 300s to 900s with 15 attempts yields +239 additional perfect solves.
- Base codes are essentially solved (96–100% per agent). The difficulty frontier lies in large tensor product codes with 100+ stabilizers and high code distance (d≥12).

---

## 1. Overall Agent Comparison

### Per-Agent, Per-Configuration Summary

| Agent | Config | N | Perfect Solve Rate | Completion Rate | Avg Success Rate | Avg Elapsed (s) | Median Elapsed (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 1 attempt, 900s | 192 | 153/192 (79.7%) | 163/192 (84.9%) | 0.833 | 370.9 | 137.7 |
| Claude Opus 4.6 | 15 attempts, 300s | 192 | 48/192 (25.0%) | 51/192 (26.6%) | 0.261 | 252.3 | 302.3 |
| Claude Opus 4.6 | 15 attempts, 900s | 192 | 140/192 (72.9%) | 144/192 (75.0%) | 0.747 | 440.4 | 236.9 |
| GPT-5.2 | 1 attempt, 900s | 192 | 154/192 (80.2%) | 161/192 (83.9%) | 0.833 | 370.1 | 140.8 |
| GPT-5.2 | 15 attempts, 300s | 192 | 46/192 (24.0%) | 51/192 (26.6%) | 0.255 | 252.9 | 302.3 |
| GPT-5.2 | 15 attempts, 900s | 192 | 137/192 (71.4%) | 139/192 (72.4%) | 0.724 | 439.7 | 230.3 |
| Gemini 3 Pro Preview | 1 attempt, 900s | 192 | 139/192 (72.4%) | 160/192 (83.3%) | 0.800 | 456.5 | 293.2 |
| Gemini 3 Pro Preview | 15 attempts, 300s | 192 | 67/192 (34.9%) | 68/192 (35.4%) | 0.354 | 250.1 | 302.3 |
| Gemini 3 Pro Preview | 15 attempts, 900s | 192 | 123/192 (64.1%) | 134/192 (69.8%) | 0.690 | 1189.8 | 400.6 |

### Agent Aggregate Summary (All Configs)

| Agent | Total Runs | Perfect Solves | Perfect Solve Rate | Completions | Completion Rate | Avg Success Rate | Avg Elapsed (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 576 | 341 | 59.2% | 358 | 62.2% | 0.614 | 354.5 |
| GPT-5.2 | 576 | 337 | 58.5% | 351 | 60.9% | 0.604 | 354.3 |
| Gemini 3 Pro Preview | 576 | 329 | 57.1% | 362 | 62.8% | 0.615 | 632.1 |

**Key observations:**

- **Best single configuration: GPT-5.2 at 1 attempt/900s** achieves the highest perfect solve rate of any agent-config pair (80.2%), followed closely by Claude (79.7%).
- **Gemini 3 Pro Preview** is slowest (632s avg across configs, vs ~354s for the others) but shows the highest completion rate (62.8%) indicating it produces more circuits even when imperfect.
- The **1 attempt/900s config is the best for all agents**, suggesting that concentrated single-shot reasoning outperforms iterative self-correction.
- The **15 attempts/300s config is by far the worst** (25–35% perfect solve rate) because 300s is insufficient for large circuits.

---

## 2. Difficulty Frontier

### Success by Stabilizer Count (Best Config Per Agent)

| Stabilizer Range | Benchmarks | Solved by Any Agent | Solved by All Agents | Avg Best Success Rate |
| --- | --- | --- | --- | --- |
| 1–2 | 5 | 5/5 (100%) | 5/5 (100%) | 1.000 |
| 3–8 | 7 | 7/7 (100%) | 6/7 (86%) | 0.992 |
| 9–14 | 2 | 2/2 (100%) | 2/2 (100%) | 1.000 |
| 15–24 | 8 | 8/8 (100%) | 8/8 (100%) | 1.000 |
| 25–50 | 48 | 48/48 (100%) | 48/48 (100%) | 1.000 |
| 51–100 | 48 | 48/48 (100%) | 44/48 (92%) | 0.986 |
| 101–200 | 74 | 60/74 (81%) | 25/74 (34%) | 0.680 |

### Success by Code Type (Best Config Per Agent)

| Code Type | Agent | Benchmarks | Perfect Solves | Perfect Rate | Avg Success |
| --- | --- | --- | --- | --- | --- |
| Base Code | Claude Opus 4.6 | 24 | 23 | 95.8% | 0.993 |
| Base Code | Gemini 3 Pro Preview | 24 | 24 | 100.0% | 1.000 |
| Base Code | GPT-5.2 | 24 | 24 | 100.0% | 1.000 |
| Tensor Product | Claude Opus 4.6 | 168 | 139 | 82.7% | 0.844 |
| Tensor Product | Gemini 3 Pro Preview | 168 | 134 | 79.8% | 0.889 |
| Tensor Product | GPT-5.2 | 168 | 135 | 80.4% | 0.832 |

### Success by Code Distance

| Distance | Benchmarks | Solved by Any | Solved by All | Avg Perfect Rate | Avg Success Rate |
| --- | --- | --- | --- | --- | --- |
| 2 | 5 | 5/5 | 5/5 | 100.0% | 1.000 |
| 3 | 8 | 8/8 | 7/8 | 95.8% | 0.993 |
| 4 | 2 | 2/2 | 2/2 | 100.0% | 1.000 |
| 5 | 3 | 3/3 | 3/3 | 100.0% | 1.000 |
| 6 | 36 | 36/36 | 36/36 | 100.0% | 1.000 |
| 7 | 4 | 4/4 | 4/4 | 100.0% | 1.000 |
| 9 | 54 | 54/54 | 49/54 | 96.9% | 0.987 |
| 10 | 15 | 15/15 | 11/15 | 86.7% | 0.955 |
| 12 | 8 | 7/8 | 4/8 | 70.8% | 0.708 |
| 14 | 13 | 8/13 | 3/13 | 46.2% | 0.536 |
| 15 | 32 | 26/32 | 13/32 | 61.5% | 0.678 |
| 21 | 12 | 10/12 | 1/12 | 44.4% | 0.640 |

### Frontier Analysis

| Entity | Total Perfect Solves | Max Stabilizers Solved | Max Qubits Solved | Max Distance Solved |
| --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 162 | 160 | 161 | 21 |
| GPT-5.2 | 159 | 174 | 175 | 21 |
| Gemini 3 Pro Preview | 158 | 184 | 185 | 21 |
| ANY AGENT | 178 | 184 | 185 | 21 |
| ALL AGENTS | 138 | 152 | 153 | 21 |

**Key observations:**

- **All codes up to 50 stabilizers are solvable** by at least one agent (often all three). This is a remarkably strong result.
- The **difficulty cliff occurs at ~100 stabilizers**: 51–100 gens are 92% solved by all agents, but 101–200 drops to 34%.
- **Base codes are essentially fully solved** (96–100% across agents). The challenge is in tensor product codes.
- **Code distance d≥12 marks the hard frontier**: d≤10 codes are 87%+ solvable; d≥12 drops to 46–62%.
- **Gemini 3 Pro Preview has the broadest reach** (solved a circuit with 184 stabilizers / 185 qubits), while **Claude has the most total solves** (162 unique codes).

---

## 3. What Makes Circuits Hard

### Hardness by Feature

| Feature | Count | Avg Best Success | Solvable by Any (%) | Solvable by All (%) |
| --- | --- | --- | --- | --- |
| Qubits 1–10 | 11 | 0.995 | 100% | 91% |
| Qubits 11–25 | 10 | 1.000 | 100% | 100% |
| Qubits 26–50 | 42 | 1.000 | 100% | 100% |
| Qubits 51–100 | 50 | 0.986 | 100% | 92% |
| Qubits 101–200 | 79 | 0.701 | 82% | 38% |
| Base Code | 24 | 0.998 | 100% | 96% |
| Tensor Product | 168 | 0.855 | 92% | 68% |
| Distance d≤3 | 13 | 0.995 | 100% | 92% |
| Distance d=6–7 | 40 | 1.000 | 100% | 100% |
| Distance d=9 | 54 | 0.987 | 100% | 91% |
| Distance d=10 | 15 | 0.955 | 100% | 73% |
| Distance d=12 | 8 | 0.708 | 88% | 50% |
| Distance d=14 | 13 | 0.536 | 62% | 23% |
| Distance d=15 | 32 | 0.678 | 81% | 41% |
| Distance d=21 | 12 | 0.640 | 83% | 8% |
| Max Weight 4–8 | 23 | 0.998 | 100% | 96% |
| Max Weight 9–15 | 39 | 0.940 | 95% | 90% |
| Max Weight 16–100 | 130 | 0.831 | 91% | 62% |

### The 14 Never-Solved Benchmarks

All 14 benchmarks that were **never** perfectly solved by any agent share these properties:
- **All are tensor product codes** (100%)
- **Qubit range:** 148–196 (median: 175)
- **Stabilizer count:** 146–194 (median: 174)
- **Distance range:** d=12 to d=21
- Examples: (Carbon) * (Golay) 184q, (Hex Color Code d=7) * (Perfect 5-Qubit Code) 185q, (Rotated Surface Code d=5) * (Steane) 175q

**The hardness factors, ranked by predictive power:**

1. **Qubit/stabilizer count** (strongest): Codes with 100+ qubits have only 82% solve rate by any agent, 38% by all.
2. **Code distance** (strong): d≥14 has only 46–62% solve rate.
3. **Tensor product structure** (moderate): Tensor products are harder (92% any vs 100% base), but many tensor products ARE solvable.
4. **Max stabilizer weight** (moderate): High-weight stabilizers (16+) correlate with 62% all-agent solve rate vs 96% for low-weight.

### 40 Partially-Solved Benchmarks (Solved by Some But Not All Agents)

These 40 codes are the "frontier" — where agent quality matters most. They are mostly tensor product codes with 80–185 qubits and d=9–21. Notably:
- **Claude Opus 4.6** solved 26/40 of these
- **GPT-5.2** solved 22/40
- **Gemini 3 Pro Preview** solved 25/40
- Only 1 base code is in this set: **Hex Color Code d=3** (solved by GPT-5.2 and Gemini, not Claude)

---

## 4. Impact of Attempts and Timeout

### 4a. Single-Shot (1 attempt) vs Iterative Reasoning (15 attempts), 900s timeout

This comparison isolates the effect of iterative agentic reasoning vs concentrated single-shot generation.

| Agent | N | 1att Perfect | 15att Perfect | Gained | Lost | Net | p-value | Δ Success |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 192 | 153 (79.7%) | 140 (72.9%) | 9 | 22 | **-13** | 0.098 (NS) | -0.086 |
| GPT-5.2 | 192 | 154 (80.2%) | 137 (71.4%) | 5 | 22 | **-17** | 0.009 | -0.109 |
| Gemini 3 Pro Preview | 192 | 139 (72.4%) | 123 (64.1%) | 18 | 34 | **-16** | 0.115 (NS) | -0.110 |
| **ALL AGENTS** | 576 | 446 (77.4%) | 400 (69.4%) | 32 | 78 | **-46** | **0.0001** | **-0.102** |

**Key insight: More attempts HURT performance.** With the same 900s timeout, 1 attempt yields 77.4% perfect solve rate vs 69.4% for 15 attempts — a statistically significant difference (p=0.0001). This is counterintuitive but reveals that:
- The overhead of each check_stabilizers call + response generation consumes valuable time
- Iterative self-correction often leads to "thrashing" between approaches rather than converging
- Extended single-shot chain-of-thought reasoning is more effective for this task than trial-and-error
- The current frontier models are strong enough that their first carefully-considered answer is often their best

### 4b. Short Timeout (300s) vs Long Timeout (900s), 15 attempts

| Agent | N | 300s Perfect | 900s Perfect | Gained | Lost | Net | p-value | Δ Success |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 192 | 48 (25.0%) | 140 (72.9%) | 92 | 0 | **+92** | <0.0001 | +0.486 |
| GPT-5.2 | 192 | 46 (24.0%) | 137 (71.4%) | 91 | 0 | **+91** | <0.0001 | +0.469 |
| Gemini 3 Pro Preview | 192 | 67 (34.9%) | 123 (64.1%) | 59 | 3 | **+56** | <0.0001 | +0.336 |
| **ALL AGENTS** | 576 | 161 (28.0%) | 400 (69.4%) | 242 | 3 | **+239** | **<0.0001** | **+0.430** |

**Key insight: Timeout is the dominant factor.** Tripling the timeout from 300s to 900s yields +239 additional perfect solves with almost zero losses. Many codes simply need more computation time, and 300s is insufficient for the iterative approach.

### 4c. Single Extended Thinking (1att/900s) vs Agentic Iteration (15att/300s)

| Agent | N | 1att/900s | 15att/300s | Gained | Lost | Net | p-value | Δ Success |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 192 | 153 (79.7%) | 48 (25.0%) | 2 | 107 | **-105** | <0.0001 | -0.571 |
| GPT-5.2 | 192 | 154 (80.2%) | 46 (24.0%) | 0 | 108 | **-108** | <0.0001 | -0.578 |
| Gemini 3 Pro Preview | 192 | 139 (72.4%) | 67 (34.9%) | 6 | 78 | **-72** | <0.0001 | -0.446 |
| **ALL AGENTS** | 576 | 446 (77.4%) | 161 (28.0%) | 8 | 293 | **-285** | **<0.0001** | **-0.532** |

**Key insight: A single extended-thinking attempt massively outperforms 15 short-timeout attempts.** This is the largest effect in the entire study. Extended single-shot reasoning with enough time (900s) achieves 2.8x the perfect solve rate of the multi-attempt short-timeout configuration.

### Summary: What Configuration Works Best?

| Rank | Config | Perfect Rate | Why |
| --- | --- | --- | --- |
| 1 | **1 attempt, 900s** | **77.4%** | Maximum time for careful reasoning; no overhead |
| 2 | 15 attempts, 900s | 69.4% | More tools available but overhead reduces effective reasoning time |
| 3 | 15 attempts, 300s | 28.0% | Insufficient time; most codes timeout |

**The takeaway:** For this task, giving the LLM more time to think deeply on a single attempt is more valuable than giving it multiple chances to iterate with verification feedback. This suggests the models' internal reasoning capabilities are more powerful than their ability to use external tool feedback for self-correction, at least for this specific circuit generation task.

---

## 5. Unique Agent Strengths

### Uniquely Solved Benchmarks

| Agent | Uniquely Solved | Examples |
| --- | --- | --- |
| **Claude Opus 4.6** | 4 codes | (Hex CC d=3) x (Golay), (Hypercube l=1) x (RSC d=5), (P5Q) x (RSC d=5), (Steane) x (Hex CC d=5) |
| **GPT-5.2** | 1 code | (SO CC d=3) x (Golay) |
| **Gemini 3 Pro Preview** | 10 codes | (Carbon) x (Tetrahedral), (Hex CC d=5) x (Shor), (Ice m=4) x (Golay), (P5Q) x (Hex CC d=7), (SO CC d=7) x (P5Q), (Steane) x (Golay), and 4 more |

### Performance by Regime (Best Config Per Agent)

| Regime | Best Agent | Their Rate | 2nd Best | Their Rate |
| --- | --- | --- | --- | --- |
| Small codes (<=10q) | GPT-5.2 / Gemini | 100.0% | Claude | 90.9% |
| Medium codes (11-25q) | All tied | 100.0% | — | — |
| Large codes (>25q) | Claude | 83.0% | GPT-5.2 | 80.7% |
| Base codes | GPT-5.2 / Gemini | 100.0% | Claude | 95.8% |
| Tensor products | Claude | 82.7% | GPT-5.2 | 80.4% |
| Low distance (d<=3) | GPT-5.2 / Gemini | 100.0% | Claude | 92.3% |
| High distance (d>=6) | Claude | 83.3% | GPT-5.2 | 81.0% |

**Pattern:** Claude Opus 4.6 is strongest on the hardest codes (large, high-distance, tensor product), while GPT-5.2 and Gemini are slightly better on easier codes. Gemini has the broadest reach (solving the largest individual code at 185 qubits).

---

## 6. Summary of Trends and Recommendations

### Main Trends

1. **All three agents are remarkably capable** at quantum circuit generation, solving 93% of benchmarks (by any agent) and reliably handling codes up to 50+ stabilizers.

2. **Base codes are functionally solved** — GPT-5.2 and Gemini achieve 100% perfect solve rate on all 24 base codes; Claude solves 23/24.

3. **Most tensor product codes are also solvable** (~80% perfect solve rate per agent, best config), overturning the expectation that these would be intractable. The agents can handle codes with up to 100 stabilizers reliably.

4. **The hard frontier is at ~100+ stabilizers with d>=12.** Below this threshold, agents succeed consistently. Above it, success drops sharply. The 14 truly intractable codes all have 146+ stabilizers and d>=12.

5. **Single-shot extended reasoning beats iterative tool use.** This is the study's most counterintuitive and important finding. With equal timeout, 1 attempt achieves 8 percentage points better performance than 15 attempts (p=0.0001). The overhead of verification tool calls and iterative reasoning is counterproductive.

6. **Timeout is the critical resource.** Going from 300s to 900s transforms 15-attempt performance from 28% to 69%. Time for reasoning — whether single-shot or iterative — is what matters most.

7. **Agent complementarity is significant.** Of 178 solved codes, 40 were solved by some but not all agents. Running all three agents and taking the best result would improve coverage from ~80% (single agent) to 93% (ensemble).

8. **Claude excels on hard codes, GPT-5.2 and Gemini on breadth.** Claude leads in tensor products and high-distance codes. Gemini has the broadest individual reach (185 qubits). GPT-5.2 is the most consistent.

### What's Currently Possible vs Not

| Category | Status | Perfect Solve Rate |
| --- | --- | --- |
| Base codes (all sizes) | Solved | 96–100% |
| Tensor products, <=100 stabilizers | Mostly solved | ~92% (by all agents) |
| Tensor products, 101–150 stabilizers | Partially solvable | ~60–80% (varies by agent) |
| Tensor products, 150+ stabilizers, d>=12 | Largely unsolvable | ~8–50% |
| Codes with 146+ stabs AND d>=12 | Never solved | 0% |

### Recommendations

1. **Prefer single-shot with long timeout over iterative attempts** — The data clearly shows that letting the agent think deeply once (1att/900s) is superior to iterative correction (15att/900s). This should inform system design and resource allocation.

2. **Ensure sufficient timeout (>=900s)** — 300s is catastrophically insufficient. For production use, allocate at least 900s per circuit, more for codes with 50+ stabilizers.

3. **Use agent ensembles for maximum coverage** — Run all three agents and select the best result. This increases coverage from ~80% to 93% with no prompt changes.

4. **Target fine-tuning at the 100–150 stabilizer range** — This is the "solvable but unreliable" zone where improved training data would have the highest ROI.

5. **For 150+ stabilizer codes, invest in algorithmic scaffolding** — Pure LLM reasoning cannot handle these. Provide specialized tools: stabilizer tableau manipulation, graph state decomposition, or tensor product decomposition (solve components independently, then compose).

6. **Investigate why iteration hurts** — The negative effect of multiple attempts is surprising and deserves deeper investigation. Hypotheses: tool-call overhead consuming reasoning time; iterative "thrashing" between approaches; model over-correcting based on partial feedback.

7. **Address Claude's base code gap** — Claude fails on 1 base code (Hex Color Code d=3) that both other agents solve. This may indicate a specific prompt engineering opportunity.

---

## Appendix: Data Files

All detailed data is available in `rq1/analysis_results/`:
- `00_detailed_results.csv` — Every result record (1,728 rows)
- `00_best_per_agent_per_code.csv` — Best result per agent per code
- `01_agent_config_summary.csv` — Agent x config aggregate stats
- `01_agent_aggregate_summary.csv` — Agent aggregate stats
- `02_difficulty_by_stabilizer_count.csv` — Success by stabilizer count
- `02_difficulty_by_code_type.csv` — Success by base vs tensor product
- `02_difficulty_by_distance.csv` — Success by code distance
- `02_frontier_analysis.csv` — Max solved by each agent
- `03_never_solved_benchmarks.csv` — The 14 never-solved codes
- `03_sometimes_solved_benchmarks.csv` — Codes solved by some agents
- `03_hardness_features.csv` — Feature-based hardness analysis
- `04_comparison_1att_vs_15att_900s.csv` — 1 vs 15 attempts comparison
- `04_comparison_300s_vs_900s_15att.csv` — 300s vs 900s timeout comparison
- `04_comparison_1att900s_vs_15att300s.csv` — Single-shot vs agentic comparison
- `05_unique_agent_strengths.csv` — Uniquely solved codes
- `05_agent_strength_by_regime.csv` — Agent performance by regime
- `analysis_report.md` — Full analysis report with all tables
