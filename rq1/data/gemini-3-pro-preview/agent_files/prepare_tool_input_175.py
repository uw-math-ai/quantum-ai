import json
import stim

# Read stabilizers
with open('data/gemini-3-pro-preview/agent_files/stabilizers_175_task.txt', 'r') as f:
    stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]

# Read circuit
with open('data/gemini-3-pro-preview/agent_files/circuit_175_candidate.stim', 'r') as f:
    circuit_str = f.read()

print(json.dumps({
    "circuit": circuit_str,
    "stabilizers": stabilizers
}))
