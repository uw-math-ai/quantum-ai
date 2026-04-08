import stim
import sys

# Read circuit
with open("final_circuit.stim", "r") as f:
    circuit_str = f.read()

c = stim.Circuit(circuit_str)
max_q = c.num_qubits
ancillas = list(range(45, max_q))

# Read stabilizers
with open("data/gemini-3-pro-preview/agent_files_ft/stabilizers_correct.txt", "r") as f:
    stabs = [l.strip().replace(',','').replace(' ','') for l in f if l.strip()]

# Call validate_circuit via print (simulated)
# In reality I use the tool.
print(f"ANCILLAS: {ancillas}")
# print(f"CIRCUIT: {circuit_str}")
