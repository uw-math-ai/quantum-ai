# StabilizerBench: Benchmarking AI-Assisted QEC Circuit Synthesis

**StabilizerBench** is a benchmark for evaluating AI agents on quantum error correction (QEC) circuit synthesis. The benchmark focuses on stabilizer circuits, which are central to QEC and can be efficiently verified using stabilizer-based oracles.

The benchmark suite contains **192 stabilizer codes** across **14 code families**, ranging from **4 to 196 qubits** and code distances **2 to 21**. It evaluates whether (1) AI agents can generate correct stabilizer state-preparation circuits, (2) optimize circuits while preserving their semantics, and (3) improve fault tolerance through flag-based circuit modifications.

All circuits use [Stim](https://github.com/quantumlib/Stim) format and are validated through automated verification tools.

## Research Questions

| # | Question | Metric |
|---|----------|--------|
| **RQ1** | Can an agent generate stabilizer circuits reliably? | % stabilizer preservation |
| **RQ2** | Can an agent make a circuit fault-tolerant? | Median FT score |
| **RQ3** | Can an agent optimize without breaking FT? | Circuit volume |
| **RQ4** | Does training/fine-tuning an LLM improve results? | Same as above |

## Structure

| Directory | Purpose |
|-----------|---------|
| `data/` | Benchmarks, datasets, and LLM evaluation results |
| `tools/` | Copilot agent, MCP verification server, prompts |
| `reinforcement_learning/` | Two-agent RL system (generator + FT enforcer) |
| `RL/` | Gymnasium env for step-by-step circuit building |
| `Examples/` | Example FT circuits and verification scripts |
| `ai_ft_prep_instructions/` | Reference FT state-prep data |

## Setup

```bash
pip install -r tools/requirements.txt
pip install -r RL/requirements.txt
```

For the Copilot agent, see [`tools/agent-readme.md`](tools/agent-readme.md). For dataset format, see [`data/DATASET_FORMAT.md`](data/DATASET_FORMAT.md).
