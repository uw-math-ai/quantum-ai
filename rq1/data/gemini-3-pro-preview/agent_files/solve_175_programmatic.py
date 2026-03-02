import stim
import numpy as np

def pauli_to_binary(p_str):
    n = len(p_str)
    x = np.zeros(n, dtype=int)
    z = np.zeros(n, dtype=int)
    for i, c in enumerate(p_str):
        if c == 'X':
            x[i] = 1
        elif c == 'Z':
            z[i] = 1
        elif c == 'Y':
            x[i] = 1
            z[i] = 1
    return x, z

with open('data/gemini-3-pro-preview/agent_files/stabilizers_175_task.txt', 'r') as f:
    stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]

# Remove duplicates
unique_stabilizers = sorted(list(set(stabilizers)))
print(f"Unique stabilizers: {len(unique_stabilizers)}")

# Convert to stim tableau
tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in unique_stabilizers], allow_underconstrained=True)
circuit = tableau.to_circuit()

# Save circuit
with open('data/gemini-3-pro-preview/agent_files/circuit_175_candidate.stim', 'w') as f:
    f.write(str(circuit))
    
print("Circuit generated.")
