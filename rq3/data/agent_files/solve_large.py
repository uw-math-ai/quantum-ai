import stim
import sys
import os

# Set up paths
baseline_path = "baseline_large.stim"
stabilizers_path = "stabilizers_large.txt"
output_path = "candidate_large.stim"

def read_stabilizers(path):
    with open(path, 'r') as f:
        # Read the file content
        content = f.read().strip()
        # Split by comma to get individual stabilizers
        stabilizer_strs = [s.strip() for s in content.split(',') if s.strip()]
        
    return stabilizer_strs

def synthesize_circuit(stabilizers):
    # Create a Tableau from stabilizers
    # Note: stim.Tableau.from_stabilizers expects a list of stim.PauliString objects
    pauli_strings = [stim.PauliString(s) for s in stabilizers]
    
    # Attempt synthesis using graph_state method
    # allow_redundant=True is often needed if stabilizers are not independent
    # allow_underconstrained=True is needed if stabilizers don't specify full state (N stabilizers for N qubits)
    # The prompt implies we must preserve these stabilizers. If they are the ONLY stabilizers, the state is underconstrained or exactly constrained.
    # The number of qubits is length of string.
    
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        return circuit
    except Exception as e:
        print(f"Synthesis failed: {e}")
        return None

def main():
    print(f"Reading stabilizers from {stabilizers_path}...")
    stabilizers = read_stabilizers(stabilizers_path)
    print(f"Found {len(stabilizers)} stabilizers.")
    
    print("Synthesizing circuit...")
    circuit = synthesize_circuit(stabilizers)
    
    if circuit:
        print(f"Synthesis successful. Circuit has {len(circuit)} instructions.")
        
        # Check if the circuit contains RX gates (which graph_state method produces for |0> start)
        # We might need to replace them with H gates if the baseline starts with |0>
        # However, stim's graph state synthesis produces a circuit that prepares the state from |0>.
        # It uses RX, CZ, SQRT_X, etc.
        # Let's save it.
        
        with open(output_path, 'w') as f:
            f.write(str(circuit))
        print(f"Written candidate to {output_path}")
        
    else:
        print("Synthesis failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
