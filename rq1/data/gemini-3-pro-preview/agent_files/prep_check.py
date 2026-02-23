import stim
import json

with open(r'data/gemini-3-pro-preview/agent_files/circuit_optimized.stim', 'r') as f:
    circuit_str = f.read()

# I need to create the JSON for check_stabilizers_tool.
# But I can't call it directly from python script here.
# I will just print the circuit length or something.

print(f"Circuit lines: {len(circuit_str.splitlines())}")
