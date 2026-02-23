import stim

# Read stabilizers from file
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gpt5.2\agent_files\stabilizers_161.txt', 'r') as f:
    stabilizers_raw = f.read().strip().split('\n')

stabilizers = [s.strip() for s in stabilizers_raw if s.strip()]
n_qubits = 161

# Convert to PauliString objects
stabs = [stim.PauliString(s) for s in stabilizers]

# Use Stim's tableau method with allow_underconstrained and allow_redundant
tab = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True, allow_redundant=True)
circuit = tab.to_circuit('elimination')

# Save circuit to file
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gpt5.2\agent_files\circuit_161.stim', 'w') as f:
    f.write(str(circuit))

print("Circuit saved to circuit_161.stim")
print(f"Circuit has {len(circuit)} instructions")

# Read the circuit back and verify it parses
circuit2 = stim.Circuit(str(circuit))
print(f"Circuit parsed successfully with {len(circuit2)} instructions")
