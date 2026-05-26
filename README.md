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
| `analysis/` | Analysis scripts, plots, and benchmark aggregation |
| `B1/` | Benchmark 1 runs, data, prompts, and results |
| `B2/` | Benchmark 2 runs, data, prompts, and results |
| `B3/` | Benchmark 3 runs, data, analysis, and scores |
| `data/` | Benchmarks, datasets, circuit generators, and LLM outputs |
| `tools/` | Copilot agent, MCP verification server, tools, and prompts |
| `docs/` | Project documentation and plans |

## Setup/Installation

### 1. Install Copilot CLI

Follow the official installation guide: https://docs.github.com/en/copilot/how-tos/copilot-cli/install-copilot-cli

### 2. Authenticate with GitHub Copilot

You need to authenticate using a Personal Access Token:

1. Create a Personal Access Token on GitHub (with appropriate scopes according to installation guide in [step 1](#1-install-copilot-cli))
2. Create a file called `.env` in the `tools/` directory
3. Add the following line to `.env`:
   ```
   GH_TOKEN=<your_personal_access_token>
   ```

This environment variable will be automatically loaded by the agent when it starts.

### 3. Install Python Dependencies

Install the required Python packages using pip (recommended inside a virtual Python environment):

```bash
pip install -r requirements.txt
```

The dependencies include:
- `stim` - Quantum circuit simulation
- `python-dotenv` - Environment variable management
- `github-copilot-sdk` - Copilot AI SDK for Python
- `fastmcp` - Fast Model Context Protocol support

### 4. (Optional) Set Up Ollama

If you want to use local Ollama models, set up and verify your Ollama installation:

```bash
python tools/ollama_setup.py --model ministral-3:8b
```

**Important:** The Copilot SDK requires models that support tool calls. Recommended Ollama models:
- `ministral-3:8b` (recommended - smaller, faster)
- `ministral-3:14b` (larger, potentially more capable)

Models like `llama3.1` or `deepseek-coder-v2` do **not** support tool calls and will not work with the Copilot SDK.

This script will:
- Check if Ollama is running
- Pull the specified model if it's not already available
- Verify the model works with a test query

You can also set environment variables in your `.env` file:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=ministral-3:8b
```

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
- `--model <name>`: Override the model for every selected benchmark (e.g. `gpt-5.2`).
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

For detailed information on the Copilot SDK and API, refer to:

- **Getting Started Guide**: https://github.com/github/copilot-sdk/blob/main/docs/getting-started.md
- **Python SDK README**: https://github.com/github/copilot-sdk/blob/main/python/README.md
- **GitHub Copilot CLI Docs**: https://docs.github.com/en/copilot/how-tos/copilot-cli/install-copilot-cli
- **Ollama Quickstart**: https://docs.ollama.com/quickstart


For dataset format, see [`data/DATASET_FORMAT.md`](data/DATASET_FORMAT.md).
