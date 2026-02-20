import stim
import sys
import os

def solve():
    # Read stabilizers
    # Using relative path from the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stabs_path = os.path.join(script_dir, "stabilizers_196.txt")
    
    with open(stabs_path, "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    print(f"Number of stabilizers: {len(stabs)}")
    
    # Check if they are valid Pauli strings
    num_qubits = len(stabs[0])
    print(f"Number of qubits inferred from length: {num_qubits}")
    
    # Create tableau
    # Note: stim.Tableau.from_stabilizers takes a list of stim.PauliString
    pauli_stabs = [stim.PauliString(s) for s in stabs]
    
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True, allow_redundant=True)
        print("Tableau creation successful.")
        
        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        
        # Output circuit
        circuit_path = os.path.join(script_dir, "circuit_196.stim")
        with open(circuit_path, "w") as f:
            f.write(str(circuit))
            
        print(f"Circuit generated at {circuit_path}")
        
    except Exception as e:
        print(f"Error creating tableau: {e}")
        # If it fails, we might need to find a consistent subset.
        # Check commutativity
        
        anticommuting_pairs = []
        for i in range(len(pauli_stabs)):
            for j in range(i + 1, len(pauli_stabs)):
                if not pauli_stabs[i].commutes(pauli_stabs[j]):
                    anticommuting_pairs.append((i, j))
        
        print(f"Number of anticommuting pairs: {len(anticommuting_pairs)}")
        if len(anticommuting_pairs) > 0:
            print("First 10 anticommuting pairs:")
            for pair in anticommuting_pairs[:10]:
                print(f"  {pair[0]} and {pair[1]}")

if __name__ == "__main__":
    solve()
