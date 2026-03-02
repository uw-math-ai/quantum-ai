import sys
import json

# Read stabilizers
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_120.txt', 'r') as f:
    stabilizers = [line.strip() for line in f if line.strip()]

# Read circuit
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_120.stim', 'r') as f:
    circuit = f.read()

# Prepare input for the tool (just to verify I have them)
print(f"Num stabilizers: {len(stabilizers)}")
print(f"Circuit length: {len(circuit)}")
