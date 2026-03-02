import stim
import sys
import os

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def solve_stabilizers(stabilizers):
    num_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)
    print(f"Solving for {num_qubits} qubits and {num_stabilizers} stabilizers.")

    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

    # Check for consistency (commutativity)
    anticommuting_pairs = []
    for i in range(num_stabilizers):
        s1 = pauli_stabilizers[i]
        for j in range(i + 1, num_stabilizers):
            s2 = pauli_stabilizers[j]
            if not s1.commutes(s2):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:10]:
             print(f"  {i} vs {j}")
        return None

    try:
        # allow_underconstrained=True because we have 48 stabilizers for 49 qubits
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        return circuit
    except Exception as e:
        print(f"Error using stim.Tableau.from_stabilizers: {e}")
        return None

if __name__ == "__main__":
    stabilizers = read_stabilizers("data/gemini-3-pro-preview/agent_files/stabilizers_49_v3.txt")
    circuit = solve_stabilizers(stabilizers)
    
    if circuit:
        with open("data/gemini-3-pro-preview/agent_files/circuit_49_v3.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit generated successfully.")
    else:
        print("Failed to generate circuit.")
