# RQ3 Experiment Summary (High-Level)

Dataset analyzed: `rq3/data/*/*.json` (7 runs, 1,344 circuits total)

## Scripts used (kept for reproducibility)

- `rq3/data/analysis/tmp_summary.py`
  - Produces high-level success/valid/better rates, condition pooling, and circuit-size buckets.
- `rq3/data/analysis/gate_swap_stats.py`
  - Quantifies whether CX reductions are true two-qubit reductions or mostly gate-type swaps.
- `rq3/data/analysis/analyze_models.py`
  - Generates model/config comparison chart and now includes 2Q-reduction and swap-like rates.

Rerun commands:

- `python rq3/data/analysis/tmp_summary.py`
- `python rq3/data/analysis/gate_swap_stats.py rq3/data`
- `python rq3/data/analysis/analyze_models.py rq3/data`

## Executive answer

Does it do what it is supposed to do (produce valid and better circuits)?

- **Yes, conditionally.**
- It performs well when given **more search budget** (15 attempts, 900s timeout).
- It performs much less reliably under tighter settings (1 attempt, or 15 attempts with 300s).

## What conditions drive success?

### 1) Runtime/search budget is the strongest condition

Pooled across available models:

- **1 attempt**: success **39.8%**
- **15 attempts / 300s**: success **39.1%**
- **15 attempts / 900s**: success **72.4%**

Interpretation:

- Increasing attempts alone was not enough at 300s.
- The large jump appears when both attempts are high **and** timeout is longer (900s).

### 2) Baseline circuit size matters (harder circuits are less often improved)

Using baseline CX count quartiles:

- **Small** circuits: success **70.3%**
- **Medium** circuits: success **61.4%**
- **Large** circuits: success **42.9%**
- **Extra-large** circuits: success **22.2%**

Interpretation:

- As circuit size grows, successful optimization probability drops.
- Large/extra-large cases likely need even more budget or a different strategy.

## Model-level high-level view

- **claude-opus-4.6**
  - 1 attempt: 26.0%
  - 15 attempts / 300s: 35.4%
  - 15 attempts / 900s: 72.9% (best)
- **gpt5.2**
  - 1 attempt: 28.1%
  - 15 attempts / 300s: 42.7%
  - 15 attempts / 900s: 71.9% (best)
- **gemini-3-pro-preview**
  - 1 attempt only available: 65.1%

## Improvement quality: real 2Q reduction vs gate-type swaps

Goal of this check:

- We do **not** want to count a change as a strong win if CX is reduced but total two-qubit operations are not reduced (e.g., CX replaced with CZ).

Definitions used:

- **True 2Q reduction**: optimized `two_qubit_gates` < baseline `two_qubit_gates`.
- **Swap-like**: optimized `cx_count` < baseline `cx_count` **but** optimized `two_qubit_gates` is not lower.
- Rates are computed **among successful cases** (`valid && better`).

Pooled result across all successful circuits:

- Successful circuits: **657**
- CX reduced within successes: **98.6%**
- True 2Q reduced within successes: **96.8%**
- Swap-like within successes: **1.8%**

Per model/config (among successful cases):

- claude-opus-4.6, 1 attempt: 2Q reduced **94.0%**, swap-like **2.0%**
- claude-opus-4.6, 15 att / 300s: 2Q reduced **97.1%**, swap-like **0.0%**
- claude-opus-4.6, 15 att / 900s: 2Q reduced **97.9%**, swap-like **1.4%**
- gemini-3-pro-preview, 1 attempt: 2Q reduced **97.6%**, swap-like **2.4%**
- gpt5.2, 1 attempt: 2Q reduced **96.3%**, swap-like **0.0%**
- gpt5.2, 15 att / 300s: 2Q reduced **98.8%**, swap-like **0.0%**
- gpt5.2, 15 att / 900s: 2Q reduced **94.9%**, swap-like **4.3%**

Interpretation:

- Most successful results are genuine reductions in multi-qubit operations.
- A small minority are swap-like improvements, so CX-only reduction is generally but not always a true two-qubit win.

## Monday-ready takeaway

- **Yes, the method works**, but **not uniformly across all conditions**.
- It is most reliable under **higher time budget (900s) with multiple attempts**.
- Success is much higher on **smaller/easier circuits** and drops on larger ones.
- For fair comparison across models, run all models under the same 15 attempts / 900s condition.
