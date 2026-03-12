import stim
import sys

def generate_graph_state_circuit():
    try:
        with open("target_stabilizers_job_v3.txt", "r") as f:
            stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]
        
        # Create PauliString objects
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Create Tableau
        # allow_redundant=True just in case, allow_underconstrained=True to fix remaining qubits to Z
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize circuit
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-processing to remove Resets and replace RX with H if necessary
        # We assume start from |0>
        # RX gate resets the qubit to X basis (+). 
        # If we start from |0>, H gate sends |0> to |+>. 
        # So RX can be replaced by H.
        # R (Reset Z) resets to |0>. If we start from |0>, this is identity (assuming no previous ops).
        
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                # Replace RX with H
                new_circuit.append("H", instr.targets_copy())
            elif instr.name == "R" or instr.name == "RY" or instr.name == "RZ":
                 # R is Reset Z. RY/RZ are other resets.
                 # If it's at the beginning, we can skip it.
                 # But graph state circuit might use them?
                 # Standard graph state synthesis usually only uses H, S, CZ, CX, etc.
                 # But let's be careful.
                 # If it's RX, it's definitely preparation of |+>.
                 if instr.name == "R":
                     pass # Ignore Reset Z as we start in |0>
                 else:
                     # Keep other instructions
                     new_circuit.append(instr)
            else:
                new_circuit.append(instr)
                
        with open("candidate_graph.stim", "w") as f:
            print(new_circuit, file=f)
        print("Written to candidate_graph.stim")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    generate_graph_state_circuit()
