import sys
import stim
import traceback

def analyze_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Number of stabilizers: {len(lines)}")
    if not lines:
        return

    num_qubits = len(lines[0])
    print(f"Number of qubits: {num_qubits}")
    
    try:
        # Convert strings to PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in lines]
        
        # Create a tableau from the stabilizers
        # allow_underconstrained=True allows < n stabilizers.
        t = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        print(f"Successfully created Tableau.")
        
        # Get the circuit.
        c = t.to_circuit()
        
        print(f"Circuit generated with {len(c)} instructions.")
        
        # Save circuit to a file
        with open("data/gemini-3-pro-preview/agent_files/circuit_candidate.stim", "w") as f:
            f.write(str(c))
            
    except Exception as e:
        print(f"Error creating Tableau/Circuit: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    analyze_stabilizers("data/gemini-3-pro-preview/agent_files/stabilizers_81.txt")
