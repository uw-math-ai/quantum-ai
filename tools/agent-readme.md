# Quantum Circuit Agent Setup Guide

This guide provides instructions for setting up and using the Copilot Agent for quantum circuit validation and generation.

## Installation

### 1. Install Copilot CLI

Follow the official installation guide: https://docs.github.com/en/copilot/how-tos/copilot-cli/install-copilot-cli

### 2. Authenticate with GitHub Copilot

You need to authenticate using a Personal Access Token:

1. Create a Personal Access Token on GitHub (with appropriate scopes)
2. Create a `.env` file in the `tools/` directory
3. Add the following line to the `.env` file:
   ```
   GH_TOKEN=<your_personal_access_token>
   ```

This environment variable will be automatically loaded by the agent when it starts.

### 3. Install Python Dependencies

Install the required Python packages using pip:

```bash
pip install -r tools/requirements.txt
```

The dependencies include:
- `stim` - Quantum circuit simulation
- `python-dotenv` - Environment variable management
- `github-copilot-sdk` - Copilot AI SDK for Python
- `fastmcp` - Fast Model Context Protocol support
- Additional quantum error correction tools

## Documentation References

For detailed information on the Copilot SDK and API, refer to:

- **Getting Started Guide**: https://github.com/github/copilot-sdk/blob/main/docs/getting-started.md
- **Python SDK README**: https://github.com/github/copilot-sdk/blob/main/python/README.md
- **GitHub Copilot CLI Docs**: https://docs.github.com/en/copilot/how-tos/copilot-cli/install-copilot-cli

## Usage

### The `prompt_agent` Function

The main entry point in `agent.py` is the `prompt_agent()` function, which sets up a fresh Copilot session to interact with an agent of your choice using provided tools and a system message.

**Function Signature:**
```python
def prompt_agent(
    prompt: str,
    system_message: str = "",
    tools: list[Tool] = [],
    model: str = "gpt-4.1",
    timeout: int | None = 60
) -> str:
```

**Parameters:**
- `prompt` - The user prompt/query to send to the agent
- `system_message` - System instructions for the agent (optional, default: empty)
- `tools` - List of Tool objects available to the agent (optional, default: empty list)
- `model` - The model to use (default: "gpt-4.1")
- `timeout` - Request timeout in seconds (default: 60)

**Returns:**
- The agent's response as a string

**Example Usage:**

```python
from agent import prompt_agent, validate_circuit

# Set up system message
system_msg = "You are a quantum circuit expert. Help validate and optimize circuits."

# Create a prompt
user_prompt = "Please validate this circuit: H 0\nCX 0 1"

# Call the agent with tools
response = prompt_agent(
    prompt=user_prompt,
    system_message=system_msg,
    tools=[validate_circuit],
    timeout=120
)

print(response)
```

## Running the Agent

To run the main agent:

```bash
python tools/agent.py
```

This will execute the `main()` function which demonstrates circuit generation with predefined stabilizers.
