# StabilizerBench: Benchmarking AI-Assisted QEC Circuit Synthesis

**StabilizerBench** is a benchmark for evaluating AI agents on quantum error correction (QEC) circuit synthesis. The benchmark focuses on stabilizer circuits, which are central to QEC and can be efficiently verified using stabilizer-based oracles.

The benchmark suite contains **192 stabilizer codes** across **14 code families**, ranging from **4 to 196 qubits** and code distances **2 to 21**. It evaluates whether (1) AI agents can generate correct stabilizer state-preparation circuits, (2) optimize circuits while preserving their semantics, and (3) improve fault tolerance through flag-based circuit modifications.

All circuits use [Stim](https://github.com/quantumlib/Stim) format and are validated through automated verification tools.

## Research Questions

The benchmark is designed to quantify the following 4 research questions about AI-assisted QEC circuit synthesis. These 4 questions guide the evaluation tasks and metrics used throughout StabilizerBench.

| # | Question | Metric |
|---|----------|--------|
| **RQ1** | Can an agent generate stabilizer circuits reliably? | % stabilizer preservation |
| **RQ2** | Can an agent make a circuit fault-tolerant? | Median FT score |
| **RQ3** | Can an agent optimize without breaking FT? | Circuit volume |
| **RQ4** | Does training/fine-tuning an LLM improve results? | Same as above |

## Benchmarks

StabilizerBench is organized into three benchmark tasks of increasing difficulty. Each task provides an agent with a circuit-synthesis or circuit-editing problem, validates the submitted Stim circuit using automated stabilizer-based oracles, and reports task-specific capability and quality metrics.

| Benchmark | Task | Description | Main metric |
|-----------|------|-------------|-------------|
| `B1` | State-preparation circuit generation | B1 tests whether an agent can synthesize a quantum circuit that prepares a specified stabilizer state. | Stabilizer preservation |
| `B2` | Circuit optimization | B2 tests whether an agent can reason about circuit equivalence to produce a more efficient implementation of the same stabilizer state. | Reduction in two-qubit gate count and depth |
| `B3` | Fault-tolerant circuit generation | B3 tests whether an agent can improve the fault tolerance of a given circuit by inserting flag gadgets that detect uncorrectable error propagation. | Fault-tolerance score |

## Structure

| Directory | Purpose |
|-----------|---------|
| `analysis/` | Analysis scripts, plots, and benchmark aggregation |
| `B1/` | Benchmark 1 runs, data, prompts, and results |
| `B2/` | Benchmark 2 runs, data, prompts, and results |
| `B3/` | Benchmark 3 runs, data, analysis, and scores |
| `data/` | Benchmarks, datasets, circuit generators, and LLM outputs |
| `tools/` | Copilot agent, MCP verification server, tools, and prompts |
| `docs/` | Project documentation and plans |

## Setup/Installation

### 1. Install Python Dependencies

Install the shared requirements in a virtual environment:

```bash
python -m pip install -r requirements.txt
```

The direct OpenAI and Anthropic harnesses use Python's standard library, so no provider-specific SDK is required. Install the Copilot dependency only when using that harness:

```bash
python -m pip install -r requirements-copilot.txt
```

### 2. Configure a Harness

The shared agent supports these harnesses, all of which execute the benchmark's verification tools locally:

| Harness | Credential in `tools/.env` | Example model |
|---|---|---|
| `openai` | `OPENAI_API_KEY=<your_openai_api_key>` | `gpt-5.2-codex` |
| `anthropic` | `ANTHROPIC_API_KEY=<your_anthropic_api_key>` | `claude-sonnet-4-5` |
| `copilot` | `GH_TOKEN=<your_github_token>` or Copilot CLI login | `gpt-5.2` |

Setup pointers:

- `openai`: Create an API key in the [OpenAI API keys page](https://platform.openai.com/api-keys), ensure the associated project has API billing and access to the selected model, then set `OPENAI_API_KEY`.
- `anthropic`: Create an API key in the [Anthropic Console](https://console.anthropic.com/settings/keys), ensure the workspace has API credits and model access, then set `ANTHROPIC_API_KEY`.
- `copilot`: Install `requirements-copilot.txt`, then either set `GH_TOKEN` for an account with an active GitHub Copilot entitlement or authenticate the bundled CLI with `.../site-packages/copilot/bin/copilot login`. See the [Copilot CLI installation guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/install-copilot-cli).

`openai` is the default harness. Select a provider and compatible model explicitly, for example:

```bash
python B1/run.py --harness anthropic --model claude-sonnet-4-5
```

For the OpenAI harness, each request and local tool invocation is printed to the terminal.

To resume an interrupted benchmark without repeating completed codes, pass its output file to the matching script:

```bash
python B1/resume.py B1/data/<model>/<timestamp>.json
python B2/resume.py B2/data/<model>/<timestamp>.json
python B3/resume.py B3/data/<model>/<timestamp>.json
```

Each resume script reuses the stored benchmark path, model, harness, attempts, timeout, and prompt path, then appends only missing codes to that output file. Add `--analyze` to `B3/resume.py` to run its post-run analysis after completion.

The dependencies include:
- `stim` - Quantum circuit simulation
- `python-dotenv` - Environment variable management
- `fastmcp` - Fast Model Context Protocol support

Optional harness dependencies:
- `requirements-copilot.txt` - `github-copilot-sdk` and bundled Copilot CLI

## Running the benchmarks (run_all.py)

The repository includes a convenience entry point to run all benchmarks from one place: `run_all.py`.
This script orchestrates `B1/run.py`, `B2/run.py`, and `B3/run.py` using the defaults defined in the script's `BENCHMARKS` table.

Basic usage:

```bash
python run_all.py                # run B1, B2, B3 with defaults
python run_all.py --dry-run      # print commands that would run, don't execute
python run_all.py --only B1 B3   # run only B1 and B3
```

Common command-line options:

- `--only B# ...`: Run only the listed benchmarks (choices: `B1`, `B2`, `B3`).
- `--model <name>`: Override the model for every selected benchmark (e.g. `gpt-5.2-codex`).
- `--harness <name>`: Select `openai`, `anthropic`, or `copilot` for every selected benchmark.
- `--attempts <n>`: Override the number of attempts per circuit for every selected benchmark.
- `--timeout <seconds>`: Override per-call timeout (seconds) for every selected benchmark.
- `--limit <n>`: Limit B2 to the first `n` circuits (ignored by B1/B3).
- `--analyze`: Enable B3's post-run cleaned/cleaned2 analysis.
- `--continue-on-error`: Keep running remaining benchmarks even if one fails (default stops on first failure).
- `--dry-run`: Print the commands that would run, then exit (useful for debugging).

Notes:

- Each benchmark has its own `run.py` under the `B1/`, `B2/`, or `B3/` directory and may accept additional benchmark-specific flags. The `run_all.py` script maps the shared overrides into those per-benchmark invocations.
- Defaults (model, attempts, timeout, etc.) are set in `run_all.py`'s `BENCHMARKS` dictionary; edit that file to change repository-wide defaults.

## Documentation References

For provider API details, consult the OpenAI Responses API, Anthropic Messages API, or GitHub Copilot SDK documentation.


For dataset format, see [`data/DATASET_FORMAT.md`](data/DATASET_FORMAT.md).
