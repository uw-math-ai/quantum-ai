import json

with open(r'data/gemini-3-pro-preview/agent_files/circuit_optimized.stim', 'r') as f:
    circuit_str = f.read()

with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]

# Format as JSON object for the tool
data = {
    'circuit': circuit_str,
    'stabilizers': stabs
}

print(json.dumps(data))
