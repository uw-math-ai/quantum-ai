# Read stabilizers
import stim
import sys

# Read stabilizers
with open(r'data\gemini-3-pro-preview\agent_files\stabilizers_155.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

# stabilizers = [stim.PauliString(line) for line in lines]
stabilizers_all = [stim.PauliString(line) for line in lines]
# Remove index 148 (line 149 in file)
stabilizers = [s for i, s in enumerate(stabilizers_all) if i != 148]

print(f"Number of qubits: {len(stabilizers[0])}")
print(f"Number of stabilizers: {len(stabilizers)}")

try:
    # Use allow_underconstrained=True because we have 154 stabilizers for 155 qubits
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=False, allow_underconstrained=True)
except Exception as e:
    print(f"Error creating tableau: {e}")
    sys.exit(1)

circuit = tableau.to_circuit()
print("Circuit generated.")

with open(r'data\gemini-3-pro-preview\agent_files\circuit_155.stim', 'w') as f:
    f.write(str(circuit))
