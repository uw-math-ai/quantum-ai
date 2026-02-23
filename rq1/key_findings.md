# Key Findings: Quantum State-Preparation Circuit Generation

## Experiment Setup

- **Task**: Generate Stim circuits that prepare stabilizer states (i.e., +1 eigenstates of all generators in a stabilizer group)
- **Agents**: Claude Opus 4.6, Gemini 3 Pro Preview, GPT-5.2
- **Benchmarks**: 192 total (24 base codes + 168 tensor product codes)
- **Configurations**: 3 per agent
  - `attempts=15, timeout=300s`
  - `attempts=1, timeout=900s`
  - `attempts=15, timeout=900s`

---

## 1. Overall Ranking

| Agent | Perfect Solve Rate | Completion Rate | Avg Success Rate | Avg Time |
|-------|-------------------|-----------------|------------------|----------|
| **Claude Opus 4.6** | 53.8% | 60.1% | 78.8% | 370.2s |
| **GPT-5.2** | 55.2% | 57.8% | 78.3% | 369.2s |
| **Gemini 3 Pro** | 57.1% | 57.5% | 74.3% | 941.3s |

Aggregated across all 3 configurations. Claude and GPT-5.2 are very close; Gemini is competitive on accuracy but ~2.5x slower.

---

## 2. Solvability Frontier

The **stabilizer count** is the dominant predictor of difficulty:

| Stabilizer Range | # Benchmarks | Solvable by ANY Agent | Solvable by ALL Agents |
|------------------|-------------|----------------------|----------------------|
| 1–60 | 73 | 73 (100%) | 71 (97%) |
| 61–100 | 45 | 44 (98%) | 30 (67%) |
| 101–150 | 43 | 33 (77%) | 2 (5%) |
| 151–200 | 31 | 9 (29%) | 0 (0%) |

- **Hard frontier**: All agents can solve benchmarks up to **132 stabilizers**
- **Soft frontier**: At least one agent can solve benchmarks up to **184 stabilizers**
- **All base codes** (24/24) are solvable; difficulty is entirely in tensor product codes

---

## 3. What Makes Circuits Hard

### 3a. Code Distance is a Strong Predictor

Tensor products involving high-distance components are hardest:

| TP Component | Stabs | Solvable as TP Component |
|-------------|-------|--------------------------|
| Rotated Surface Code d=7 | 48 | 0% |
| Hex Color Code d=7 | 36 | 25% |
| Square Octagon Color Code d=7 | 30 | 33% |
| Rotated Surface Code d=5 | 24 | 49% |
| Hex Color Code d=5 | 18 | 59% |
| Golay (d=7) | 22 | 62% |

**Pattern**: d=7 topological codes make tensor products nearly unsolvable. d=5 codes create the transition zone. d=3 codes are generally manageable.

### 3b. Universally Unsolved Benchmarks

**14 benchmarks** were never solved by any agent in any configuration:
- All are tensor products with ≥146 stabilizers
- Most common hard components: Rotated Surface Code (8 appearances), Hex Color Code (5), Square Octagon Color Code (4)
- Qubit range: 148–196

### 3c. Base Codes vs. Tensor Products

| Category | Claude | Gemini | GPT-5.2 |
|----------|--------|--------|---------|
| Base codes (24) | 23/24 perfect | 23/24 perfect | **24/24 perfect** |
| Tensor products (168) | 117/168 (70%) | 100/168 (60%) | 113/168 (67%) |

---

## 4. Impact of Attempts: More Attempts **Hurts** Performance

Comparing `attempts=1` vs `attempts=15` (both with 900s timeout):

| Agent | Perfect @ 1 attempt | Perfect @ 15 attempts | Net Change | p-value |
|-------|--------------------|-----------------------|------------|---------|
| Claude | 153 (79.7%) | 140 (72.9%) | **−13** | 0.031* |
| Gemini | 139 (72.4%) | 123 (64.1%) | **−16** | 0.038* |
| GPT-5.2 | 154 (80.2%) | 137 (71.4%) | **−17** | 0.002** |

All regressions are statistically significant (McNemar's test, p < 0.05).

**The damage is concentrated in hard benchmarks (101–200 stabilizers)**:
- Claude: −16 net in this range
- Gemini: −13 net
- GPT-5.2: −17 net

**Interpretation**: With 15 attempts, agents waste time on failed retries for hard benchmarks, potentially exhausting their context window or timeout budget. A single focused attempt is more effective than iterative retrying.

---

## 5. Impact of Timeout: Longer Timeout **Massively Helps**

Comparing 300s vs 900s timeout (both with 15 attempts):

| Agent | Perfect @ 300s | Perfect @ 900s | Improvement | Regressions |
|-------|---------------|----------------|-------------|-------------|
| Claude | 48 (25.0%) | 140 (72.9%) | **+92** | 0 |
| GPT-5.2 | 46 (24.0%) | 137 (71.4%) | **+91** | 0 |
| Gemini | 67 (34.9%) | 123 (64.1%) | **+56** | 3 |

All highly significant (p ≈ 0). **Timeout is the binding constraint, not number of attempts.** Zero regressions for Claude and GPT-5.2 means every benchmark that was solvable at 300s remained solvable at 900s.

---

## 6. Unique Agent Strengths

Each agent solves some benchmarks that the others cannot (config: attempts=15, timeout=900s):

- **Gemini**: 8 uniquely solved, including the **largest** benchmarks (up to 184 stabilizers). Strongest on very large tensor products.
- **Claude**: 6 uniquely solved (98–132 stabilizers). Strongest in the transition zone.
- **GPT-5.2**: 5 uniquely solved (104–130 stabilizers). Most consistent on base codes (24/24 perfect).

### Partial Solves (near-misses)

| Agent | Partial Solves | Behavior |
|-------|---------------|----------|
| GPT-5.2 | 2 | Binary: either solves perfectly or fails completely |
| Claude | 4 | Mostly binary with a few near-misses (≥98%) |
| Gemini | 10 | More gradual degradation, several at 83–99% |

---

## 7. Summary of Trends

1. **Stabilizer count is the key difficulty metric** — not raw qubit count. The transition from "easy" to "impossible" happens between ~100 and ~150 stabilizers.

2. **Code distance drives tensor product difficulty** — d=7 components make products nearly unsolvable; d=3 components are manageable regardless of partner.

3. **Single-shot is better than iterative** — agents perform significantly better with 1 focused attempt than 15 attempts, suggesting that retry loops degrade performance (likely via context pollution or wasted time budget).

4. **Time budget matters most** — tripling the timeout from 300s to 900s nearly triples the number of perfect solves with zero regressions.

5. **No agent dominates** — Claude and GPT-5.2 are neck-and-neck overall; Gemini is slower but uniquely capable on the hardest benchmarks. An ensemble approach (union of all agents) would solve 178/192 benchmarks (93%).

6. **14 benchmarks remain completely unsolvable** by any current agent — all tensor products with ≥146 stabilizers involving high-distance topological codes.
