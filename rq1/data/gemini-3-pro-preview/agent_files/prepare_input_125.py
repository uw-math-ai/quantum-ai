import sys
import os
import json

agent_files_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files'
sys.path.append(agent_files_path)

# Importing the module will execute its top-level code
import generate_circuit_125

circuit_str = str(generate_circuit_125.circuit)
stabilizers_list = [str(s) for s in generate_circuit_125.stabilizers]

output_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\tool_input_125.json'
with open(output_path, 'w') as f:
    json.dump({'circuit': circuit_str, 'stabilizers': stabilizers_list}, f)

print(f"JSON written to {output_path}")
