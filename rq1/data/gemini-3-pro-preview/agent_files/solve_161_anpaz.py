import stim
import sys

def solve():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_161.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Number of stabilizers: {len(lines)}")
    num_qubits = len(lines[0].strip())
    print(f"Number of qubits: {num_qubits}")

    stabilizers = []
    for line in lines:
        s = line.strip()
        if len(s) != num_qubits:
            if len(s) > num_qubits:
                # print(f"Truncating stabilizer from {len(s)} to {num_qubits}")
                s = s[:num_qubits]
            else:
                # print(f"Padding stabilizer from {len(s)} to {num_qubits}")
                s = s.ljust(num_qubits, 'I')
        stabilizers.append(stim.PauliString(s))
        
    # Reorder to prioritize failing ones (last block and line 23)
    # Indices 146 to end, and 23.
    # Actually, let's just shuffle or put specific ones first.
    prioritized_indices = list(range(145, len(stabilizers))) + [23]
    other_indices = [i for i in range(len(stabilizers)) if i not in prioritized_indices]
    
    new_stabilizers = [stabilizers[i] for i in prioritized_indices] + [stabilizers[i] for i in other_indices]
    stabilizers = new_stabilizers
    
    # Save corrected stabilizers
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_161_fixed.txt", "w") as f:
        for s in stabilizers:
            f.write(str(s) + "\n")

    # Check if we have 161 stabilizers for 161 qubits
    if len(stabilizers) != num_qubits:
        print(f"Warning: Number of stabilizers ({len(stabilizers)}) does not match number of qubits ({num_qubits})")

    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        print("Successfully created tableau from stabilizers.")
        circuit = tableau.to_circuit()
        print("Generated circuit.")
        
        # Save circuit to file
        with open("data/gemini-3-pro-preview/agent_files/circuit_161.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Failed to create tableau: {e}")

if __name__ == "__main__":
    solve()
