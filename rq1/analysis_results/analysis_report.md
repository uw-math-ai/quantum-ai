# Quantum State-Preparation Circuit Benchmark: Detailed Analysis

**Date:** 2026-02-23

**Benchmarks:** 192 stabilizer codes (24 base + 168 tensor product)

**Agents:** Claude Opus 4.6, GPT-5.2, Gemini 3 Pro Preview

**Configurations:** 3 per agent (15att/300s, 1att/900s, 15att/900s)

**Total result records:** 1728


---


## 1. Overall Agent Comparison


### Per-Agent, Per-Configuration Summary

| Agent | Config | N | Perfect Solve Rate | Completion Rate | Avg Success Rate | Avg Elapsed (s) | Median Elapsed (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 1 attempt(s), 900s timeout | 192 | 153/192 (79.7%) | 163/192 (84.9%) | 0.833 | 370.9 | 137.7 |
| Claude Opus 4.6 | 15 attempt(s), 300s timeout | 192 | 48/192 (25.0%) | 51/192 (26.6%) | 0.261 | 252.3 | 302.3 |
| Claude Opus 4.6 | 15 attempt(s), 900s timeout | 192 | 140/192 (72.9%) | 144/192 (75.0%) | 0.747 | 440.4 | 236.9 |
| GPT-5.2 | 1 attempt(s), 900s timeout | 192 | 154/192 (80.2%) | 161/192 (83.9%) | 0.833 | 370.1 | 140.8 |
| GPT-5.2 | 15 attempt(s), 300s timeout | 192 | 46/192 (24.0%) | 51/192 (26.6%) | 0.255 | 252.9 | 302.3 |
| GPT-5.2 | 15 attempt(s), 900s timeout | 192 | 137/192 (71.4%) | 139/192 (72.4%) | 0.724 | 439.7 | 230.3 |
| Gemini 3 Pro Preview | 1 attempt(s), 900s timeout | 192 | 139/192 (72.4%) | 160/192 (83.3%) | 0.800 | 456.5 | 293.2 |
| Gemini 3 Pro Preview | 15 attempt(s), 300s timeout | 192 | 67/192 (34.9%) | 68/192 (35.4%) | 0.354 | 250.1 | 302.3 |
| Gemini 3 Pro Preview | 15 attempt(s), 900s timeout | 192 | 123/192 (64.1%) | 134/192 (69.8%) | 0.690 | 1189.8 | 400.6 |



### Agent Aggregate (All Configs Combined)

| Agent | Total Runs | Perfect Solves | Perfect Solve Rate | Completions | Completion Rate | Avg Success Rate | Avg Elapsed (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 576 | 341 | 59.2% | 358 | 62.2% | 0.614 | 354.5 |
| GPT-5.2 | 576 | 337 | 58.5% | 351 | 60.9% | 0.604 | 354.3 |
| Gemini 3 Pro Preview | 576 | 329 | 57.1% | 362 | 62.8% | 0.615 | 632.1 |


---


## 2. Difficulty Frontier


### Success by Stabilizer Count Range

| Stabilizer Range | Benchmarks | Solved by Any Agent | Solved by All Agents | Avg Best Success Rate |
| --- | --- | --- | --- | --- |
| 1-2 | 5 | 5/5 (100%) | 5/5 (100%) | 1.000 |
| 3-8 | 7 | 7/7 (100%) | 6/7 (86%) | 0.992 |
| 9-14 | 2 | 2/2 (100%) | 2/2 (100%) | 1.000 |
| 15-24 | 8 | 8/8 (100%) | 8/8 (100%) | 1.000 |
| 25-50 | 48 | 48/48 (100%) | 48/48 (100%) | 1.000 |
| 51-100 | 48 | 48/48 (100%) | 44/48 (92%) | 0.986 |
| 101-200 | 74 | 60/74 (81%) | 25/74 (34%) | 0.680 |



### Success by Code Type (Best Config per Agent)

| Code Type | Agent | Benchmarks | Perfect Solves | Perfect Solve Rate | Avg Success Rate |
| --- | --- | --- | --- | --- | --- |
| Base Code | Claude Opus 4.6 | 24 | 23 | 95.8% | 0.993 |
| Base Code | Gemini 3 Pro Preview | 24 | 24 | 100.0% | 1.000 |
| Base Code | GPT-5.2 | 24 | 24 | 100.0% | 1.000 |
| Tensor Product | Claude Opus 4.6 | 168 | 139 | 82.7% | 0.844 |
| Tensor Product | Gemini 3 Pro Preview | 168 | 134 | 79.8% | 0.889 |
| Tensor Product | GPT-5.2 | 168 | 135 | 80.4% | 0.832 |



### Success by Code Distance

| Distance | Benchmarks | Solved by Any | Solved by All | Avg Perfect Rate (all agents) | Avg Success Rate (all agents) |
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

| Agent | Total Perfect Solves | Max Stabilizers Solved | Max Qubits Solved | Max Distance Solved |
| --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 162 | 160 | 161 | 21 |
| GPT-5.2 | 159 | 174 | 175 | 21 |
| Gemini 3 Pro Preview | 158 | 184 | 185 | 21 |
| ANY AGENT | 178 | 184 | 185 | 21 |
| ALL AGENTS | 138 | 152 | 153 | 21 |


---


## 3. What Makes Circuits Hard


### Hardness by Feature

| Feature | Count | Avg Best Success | Any Perfect % | All Perfect % |
| --- | --- | --- | --- | --- |
| Qubits 1-10 | 11 | 0.995 | 100% | 91% |
| Qubits 11-25 | 10 | 1.000 | 100% | 100% |
| Qubits 26-50 | 42 | 1.000 | 100% | 100% |
| Qubits 51-100 | 50 | 0.986 | 100% | 92% |
| Qubits 101-200 | 79 | 0.701 | 82% | 38% |
| Base Code | 24 | 0.998 | 100% | 96% |
| Tensor Product | 168 | 0.855 | 92% | 68% |
| Distance d=2 | 5 | 1.000 | 100% | 100% |
| Distance d=3 | 8 | 0.993 | 100% | 88% |
| Distance d=4 | 2 | 1.000 | 100% | 100% |
| Distance d=5 | 3 | 1.000 | 100% | 100% |
| Distance d=6 | 36 | 1.000 | 100% | 100% |
| Distance d=7 | 4 | 1.000 | 100% | 100% |
| Distance d=9 | 54 | 0.987 | 100% | 91% |
| Distance d=10 | 15 | 0.955 | 100% | 73% |
| Distance d=12 | 8 | 0.708 | 88% | 50% |
| Distance d=14 | 13 | 0.536 | 62% | 23% |
| Distance d=15 | 32 | 0.678 | 81% | 41% |
| Distance d=21 | 12 | 0.640 | 83% | 8% |
| Max Weight 4-8 | 23 | 0.998 | 100% | 96% |
| Max Weight 9-15 | 39 | 0.940 | 95% | 90% |
| Max Weight 16-100 | 130 | 0.831 | 91% | 62% |



### Never Solved Benchmarks (showing first 30 of 14)

| Code Name | Qubits | Generators | Distance | Tensor Product | Max Weight |
| --- | --- | --- | --- | --- | --- |
| (Iceberg Code m=2) * (Hex Color Code d=7) | 148 | 146 | 14 | Yes | 28 |
| (Perfect 5-Qubit Code) * (Square Octagon Color Code d=7) | 155 | 154 | 21 | Yes | 28 |
| (Hypercube Code l=2) * (Perfect 5-Qubit Code) | 180 | 164 | 12 | Yes | 60 |
| (Hex Color Code d=5) * (Rotated Surface Code d=3) | 171 | 170 | 15 | Yes | 18 |
| (Rotated Surface Code d=3) * (Hex Color Code d=5) | 171 | 170 | 15 | Yes | 20 |
| (Steane) * (Rotated Surface Code d=5) | 175 | 174 | 15 | Yes | 28 |
| (Hex Color Code d=3) * (Rotated Surface Code d=5) | 175 | 174 | 15 | Yes | 28 |
| (Rotated Surface Code d=5) * (Steane) | 175 | 174 | 15 | Yes | 12 |
| (Rotated Surface Code d=5) * (Square Octagon Color Code d=3) | 175 | 174 | 15 | Yes | 12 |
| (Iceberg Code m=3) * (Square Octagon Color Code d=7) | 186 | 182 | 14 | Yes | 42 |
| (Hypercube Code l=1) * (Square Octagon Color Code d=7) | 186 | 182 | 14 | Yes | 42 |
| (Hex Color Code d=7) * (Perfect 5-Qubit Code) | 185 | 184 | 21 | Yes | 30 |
| (Iceberg Code m=2) * (Rotated Surface Code d=7) | 196 | 194 | 14 | Yes | 36 |
| (4-Qubit Detector Code) * (Rotated Surface Code d=7) | 196 | 194 | 14 | Yes | 36 |



### Benchmarks Solved by Some But Not All Agents

| Code Name | Qubits | Generators | Distance | Tensor Product | Solved By |
| --- | --- | --- | --- | --- | --- |
| (4-Qubit Detector Code) * (Hex Color Code d=7) | 148 | 146 | 14 | Yes | Claude Opus 4.6, Gemini 3 Pro Preview |
| (4-Qubit Detector Code) * (Rotated Surface Code d=5) | 100 | 98 | 10 | Yes | Claude Opus 4.6, Gemini 3 Pro Preview |
| (4-Qubit Detector Code) * (Square Octagon Color Code d=7) | 124 | 122 | 14 | Yes | Claude Opus 4.6, Gemini 3 Pro Preview |
| (Carbon) * (Rotated Surface Code d=3) | 108 | 106 | 12 | Yes | GPT-5.2, Gemini 3 Pro Preview |
| (Carbon) * (Shor) | 108 | 106 | 12 | Yes | Claude Opus 4.6, Gemini 3 Pro Preview |
| (Carbon) * (Tetrahedral) | 180 | 178 | 12 | Yes | Gemini 3 Pro Preview |
| (Golay) * (Hex Color Code d=3) | 161 | 160 | 21 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Golay) * (Perfect 5-Qubit Code) | 115 | 114 | 21 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Golay) * (Square Octagon Color Code d=3) | 161 | 160 | 21 | Yes | GPT-5.2, Gemini 3 Pro Preview |
| (Golay) * (Steane) | 161 | 160 | 21 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Hamming) * (Rotated Surface Code d=3) | 135 | 128 | 9 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Hex Color Code d=3) * (Golay) | 161 | 160 | 21 | Yes | Claude Opus 4.6 |
| (Hex Color Code d=3) * (Square Octagon Color Code d=5) | 119 | 118 | 15 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Hex Color Code d=3) * (Tetrahedral) | 105 | 104 | 9 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Hex Color Code d=5) * (Hex Color Code d=3) | 133 | 132 | 15 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Hex Color Code d=5) * (Shor) | 171 | 170 | 15 | Yes | Gemini 3 Pro Preview |
| (Hypercube Code l=1) * (Golay) | 138 | 134 | 14 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Hypercube Code l=1) * (Rotated Surface Code d=5) | 150 | 146 | 10 | Yes | Claude Opus 4.6 |
| (Iceberg Code m=2) * (Rotated Surface Code d=5) | 100 | 98 | 10 | Yes | Gemini 3 Pro Preview |
| (Iceberg Code m=3) * (Golay) | 138 | 134 | 14 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Iceberg Code m=3) * (Rotated Surface Code d=5) | 150 | 146 | 10 | Yes | Claude Opus 4.6, Gemini 3 Pro Preview |
| (Iceberg Code m=4) * (Golay) | 184 | 178 | 14 | Yes | Gemini 3 Pro Preview |
| (Perfect 5-Qubit Code) * (Hex Color Code d=7) | 185 | 184 | 21 | Yes | Gemini 3 Pro Preview |
| (Perfect 5-Qubit Code) * (Rotated Surface Code d=5) | 125 | 124 | 15 | Yes | Claude Opus 4.6 |
| (Perfect 5-Qubit Code) * (Square Octagon Color Code d=5) | 85 | 84 | 15 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Rotated Surface Code d=3) * (Shor) | 81 | 80 | 9 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Rotated Surface Code d=5) * (Hex Color Code d=3) | 175 | 174 | 15 | Yes | GPT-5.2, Gemini 3 Pro Preview |
| (Rotated Surface Code d=5) * (Perfect 5-Qubit Code) | 125 | 124 | 15 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Shor) * (Hex Color Code d=5) | 171 | 170 | 15 | Yes | Gemini 3 Pro Preview |
| (Shor) * (Square Octagon Color Code d=5) | 153 | 152 | 15 | Yes | Gemini 3 Pro Preview |
| (Square Octagon Color Code d=3) * (Golay) | 161 | 160 | 21 | Yes | GPT-5.2 |
| (Square Octagon Color Code d=3) * (Hex Color Code d=5) | 133 | 132 | 15 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Square Octagon Color Code d=3) * (Rotated Surface Code d=5) | 175 | 174 | 15 | Yes | Gemini 3 Pro Preview |
| (Square Octagon Color Code d=3) * (Tetrahedral) | 105 | 104 | 9 | Yes | Claude Opus 4.6, GPT-5.2 |
| (Square Octagon Color Code d=5) * (Rotated Surface Code d=3) | 153 | 152 | 15 | Yes | GPT-5.2, Gemini 3 Pro Preview |
| (Square Octagon Color Code d=7) * (Perfect 5-Qubit Code) | 155 | 154 | 21 | Yes | Gemini 3 Pro Preview |
| (Steane) * (Golay) | 161 | 160 | 21 | Yes | Gemini 3 Pro Preview |
| (Steane) * (Hex Color Code d=5) | 133 | 132 | 15 | Yes | Claude Opus 4.6 |
| (Tetrahedral) * (Rotated Surface Code d=3) | 135 | 134 | 9 | Yes | Claude Opus 4.6, GPT-5.2 |
| Hex Color Code d=3 | 7 | 6 | 3 | No | GPT-5.2, Gemini 3 Pro Preview |


---


## 4. Impact of Attempts and Timeout


### Comparison: 1 Attempt vs 15 Attempts (900s timeout)

| Agent | N | Baseline Perfect | Treatment Perfect | Gained | Lost | Net Change | p-value (McNemar) | Baseline Avg Success | Treatment Avg Success | Delta Avg Success | Baseline Avg Time (s) | Treatment Avg Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 192 | 153/192 (79.7%) | 140/192 (72.9%) | 9 | 22 | -13 | 0.0980 (NS) | 0.833 | 0.747 | -0.086 | 370.9 | 440.4 |
| GPT-5.2 | 192 | 154/192 (80.2%) | 137/192 (71.4%) | 5 | 22 | -17 | 0.0087 | 0.833 | 0.724 | -0.109 | 370.1 | 439.7 |
| Gemini 3 Pro Preview | 192 | 139/192 (72.4%) | 123/192 (64.1%) | 18 | 34 | -16 | 0.1149 (NS) | 0.800 | 0.690 | -0.110 | 456.5 | 1189.8 |
| ALL AGENTS | 576 | 446/576 (77.4%) | 400/576 (69.4%) | 32 | 78 | -46 | 0.0001 | 0.822 | 0.720 | -0.102 | 399.1 | 690.0 |



### Comparison: 300s vs 900s Timeout (15 attempts)

| Agent | N | Baseline Perfect | Treatment Perfect | Gained | Lost | Net Change | p-value (McNemar) | Baseline Avg Success | Treatment Avg Success | Delta Avg Success | Baseline Avg Time (s) | Treatment Avg Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 192 | 48/192 (25.0%) | 140/192 (72.9%) | 92 | 0 | +92 | 0.0000 | 0.261 | 0.747 | +0.486 | 252.3 | 440.4 |
| GPT-5.2 | 192 | 46/192 (24.0%) | 137/192 (71.4%) | 91 | 0 | +91 | 0.0000 | 0.255 | 0.724 | +0.469 | 252.9 | 439.7 |
| Gemini 3 Pro Preview | 192 | 67/192 (34.9%) | 123/192 (64.1%) | 59 | 3 | +56 | 0.0000 | 0.354 | 0.690 | +0.336 | 250.1 | 1189.8 |
| ALL AGENTS | 576 | 161/576 (28.0%) | 400/576 (69.4%) | 242 | 3 | +239 | 0.0000 | 0.290 | 0.720 | +0.430 | 251.8 | 690.0 |



### Comparison: 1att/900s vs 15att/300s (Reasoning vs Pure LLM)

| Agent | N | Baseline Perfect | Treatment Perfect | Gained | Lost | Net Change | p-value (McNemar) | Baseline Avg Success | Treatment Avg Success | Delta Avg Success | Baseline Avg Time (s) | Treatment Avg Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | 192 | 153/192 (79.7%) | 48/192 (25.0%) | 2 | 107 | -105 | 0.0000 | 0.833 | 0.261 | -0.571 | 370.9 | 252.3 |
| GPT-5.2 | 192 | 154/192 (80.2%) | 46/192 (24.0%) | 0 | 108 | -108 | 0.0000 | 0.833 | 0.255 | -0.578 | 370.1 | 252.9 |
| Gemini 3 Pro Preview | 192 | 139/192 (72.4%) | 67/192 (34.9%) | 6 | 78 | -72 | 0.0000 | 0.800 | 0.354 | -0.446 | 456.5 | 250.1 |
| ALL AGENTS | 576 | 446/576 (77.4%) | 161/576 (28.0%) | 8 | 293 | -285 | 0.0000 | 0.822 | 0.290 | -0.532 | 399.1 | 251.8 |


---


## 5. Unique Agent Strengths


### Benchmarks Uniquely Solved by Each Agent

| Agent | Code Name | Qubits | Generators | Distance | Tensor Product |
| --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | (Hex Color Code d=3) * (Golay) | 161 | 160 | 21 | Yes |
| Claude Opus 4.6 | (Hypercube Code l=1) * (Rotated Surface Code d=5) | 150 | 146 | 10 | Yes |
| Claude Opus 4.6 | (Perfect 5-Qubit Code) * (Rotated Surface Code d=5) | 125 | 124 | 15 | Yes |
| Claude Opus 4.6 | (Steane) * (Hex Color Code d=5) | 133 | 132 | 15 | Yes |
| GPT-5.2 | (Square Octagon Color Code d=3) * (Golay) | 161 | 160 | 21 | Yes |
| Gemini 3 Pro Preview | (Carbon) * (Tetrahedral) | 180 | 178 | 12 | Yes |
| Gemini 3 Pro Preview | (Hex Color Code d=5) * (Shor) | 171 | 170 | 15 | Yes |
| Gemini 3 Pro Preview | (Iceberg Code m=2) * (Rotated Surface Code d=5) | 100 | 98 | 10 | Yes |
| Gemini 3 Pro Preview | (Iceberg Code m=4) * (Golay) | 184 | 178 | 14 | Yes |
| Gemini 3 Pro Preview | (Perfect 5-Qubit Code) * (Hex Color Code d=7) | 185 | 184 | 21 | Yes |
| Gemini 3 Pro Preview | (Shor) * (Hex Color Code d=5) | 171 | 170 | 15 | Yes |
| Gemini 3 Pro Preview | (Shor) * (Square Octagon Color Code d=5) | 153 | 152 | 15 | Yes |
| Gemini 3 Pro Preview | (Square Octagon Color Code d=3) * (Rotated Surface Code d=5) | 175 | 174 | 15 | Yes |
| Gemini 3 Pro Preview | (Square Octagon Color Code d=7) * (Perfect 5-Qubit Code) | 155 | 154 | 21 | Yes |
| Gemini 3 Pro Preview | (Steane) * (Golay) | 161 | 160 | 21 | Yes |



### Agent Performance by Regime

| Regime | Agent | Perfect Solves | Perfect Rate | Avg Success | Best in Regime |
| --- | --- | --- | --- | --- | --- |
| Small codes (<=10 qubits) | Claude Opus 4.6 | 10/11 | 90.9% | 0.985 |  |
| Small codes (<=10 qubits) | GPT-5.2 | 11/11 | 100.0% | 1.000 |  |
| Small codes (<=10 qubits) | Gemini 3 Pro Preview | 11/11 | 100.0% | 1.000 | *** |
| Medium codes (11-25 qubits) | Claude Opus 4.6 | 10/10 | 100.0% | 1.000 | *** |
| Medium codes (11-25 qubits) | GPT-5.2 | 10/10 | 100.0% | 1.000 |  |
| Medium codes (11-25 qubits) | Gemini 3 Pro Preview | 10/10 | 100.0% | 1.000 |  |
| Large codes (>25 qubits) | Claude Opus 4.6 | 142/171 | 83.0% | 0.847 | *** |
| Large codes (>25 qubits) | GPT-5.2 | 138/171 | 80.7% | 0.835 |  |
| Large codes (>25 qubits) | Gemini 3 Pro Preview | 137/171 | 80.1% | 0.891 |  |
| Base codes | Claude Opus 4.6 | 23/24 | 95.8% | 0.993 |  |
| Base codes | GPT-5.2 | 24/24 | 100.0% | 1.000 |  |
| Base codes | Gemini 3 Pro Preview | 24/24 | 100.0% | 1.000 | *** |
| Tensor product codes | Claude Opus 4.6 | 139/168 | 82.7% | 0.844 | *** |
| Tensor product codes | GPT-5.2 | 135/168 | 80.4% | 0.832 |  |
| Tensor product codes | Gemini 3 Pro Preview | 134/168 | 79.8% | 0.889 |  |
| Low distance (d<=3) | Claude Opus 4.6 | 12/13 | 92.3% | 0.987 |  |
| Low distance (d<=3) | GPT-5.2 | 13/13 | 100.0% | 1.000 |  |
| Low distance (d<=3) | Gemini 3 Pro Preview | 13/13 | 100.0% | 1.000 | *** |
| High distance (d>=6) | Claude Opus 4.6 | 145/174 | 83.3% | 0.850 | *** |
| High distance (d>=6) | GPT-5.2 | 141/174 | 81.0% | 0.838 |  |
| High distance (d>=6) | Gemini 3 Pro Preview | 140/174 | 80.5% | 0.893 |  |