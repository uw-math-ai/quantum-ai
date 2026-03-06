
import sys
import os
import json

# Add the directory to sys.path
sys.path.append(os.path.join(os.getcwd()))

# Read fixed stabilizers
with open(os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files', 'stabilizers_175_fixed.txt'), 'r') as f:
    stabilizers = [line.strip() for line in f]

# Read circuit
with open(os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files', 'circuit_175.stim'), 'r') as f:
    circuit = f.read()

# Prepare input for check_stabilizers_tool
input_data = {
    "circuit": circuit,
    "stabilizers": stabilizers
}

# Write to a file to pass to the tool via powershell if needed, but I can call the tool directly.
# But wait, I am the agent. I call the tool `check_stabilizers_tool`.
# I don't need this script to call the tool.
# I just need the data to put in the tool call.

# I will print the first few stabilizers to verify they are loaded
print(f"Loaded {len(stabilizers)} stabilizers.")
print(f"Circuit length: {len(circuit)} chars.")
