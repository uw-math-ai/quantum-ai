# AI-Driven Quantum Error Correction Circuit Synthesis

Can AI agents generate fault-tolerant quantum error correction circuits? This repo benchmarks LLMs and reinforcement learning on synthesizing, verifying, and optimizing stabilizer-code circuits for state preparation and syndrome extraction. All circuits use [Stim](https://github.com/quantumlib/Stim) format and are validated via stabilizer-based oracles.

See the [research poster](AI-Driven%20Quantum%20Error%20Correction%20Circuit%20Synthesis.pdf) for details.

## Research Questions

| # | Question | Metric |
|---|----------|--------|
| **RQ1** | Can an agent generate stabilizer circuits reliably? | % fault-tolerant |
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
