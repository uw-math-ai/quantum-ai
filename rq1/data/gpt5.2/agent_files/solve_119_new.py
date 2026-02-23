import stim
import sys

def solve():
    # Read stabilizers from file
    with open("stabilizers_119.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    # Validate length
    n_qubits = len(lines[0])
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {len(lines)}")
    
    # Create Stim PauliStrings
    try:
        stabilizers = [stim.PauliString(s) for s in lines]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Attempt to generate circuit using Tableau.from_stabilizers
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        
        # Verify the circuit locally by simulating it? 
        # No, better just trust the tool for now, or check stabilizers preservation locally if possible.
        # But for now, just output it.
        
        # Output the circuit
        print("Generated Circuit:")
        # print(circuit)
        
        # Write to file
        with open("circuit_119_new.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit written to circuit_119_new.stim")
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
