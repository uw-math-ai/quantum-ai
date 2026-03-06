import stim
import sys

def solve():
    # Read stabilizers
    with open('data/stabilizers_105.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Convert to stim PauliStrings
    try:
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Check length
    print(f"Stabilizer length: {len(pauli_stabilizers[0])}")

    # Check commutativity
    anticommuting_pairs = []
    for i in range(len(pauli_stabilizers)):
        for j in range(i + 1, len(pauli_stabilizers)):
            if not pauli_stabilizers[i].commutes(pauli_stabilizers[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:5]:
            print(f"  {i} and {j} anticommute")
    else:
        print("All stabilizers commute.")

    # Try to generate tableau
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
        print("Successfully generated tableau.")
        
        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        print("Successfully generated circuit.")
        
        # Save circuit to file
        with open('data/gemini-3-pro-preview/agent_files/circuit_105_gemini.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating tableau: {e}")

if __name__ == "__main__":
    solve()
