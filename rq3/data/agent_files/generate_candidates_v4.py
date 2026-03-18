import stim
import os

def generate_candidates():
    # Read stabilizers
    with open("target_stabilizers_v4.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse stabilizers
    stabilizers = [stim.PauliString(line) for line in lines]
    
    # Check dimensions
    num_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)
    print(f"Loaded {num_stabilizers} stabilizers for {num_qubits} qubits")
    
    # Try to form a Tableau
    # If num_stabilizers < num_qubits, we can't make a unique tableau directly
    # But to_circuit expects a Tableau
    # If it is a stabilizer state, num_stabilizers should be equal to num_qubits
    
    if num_stabilizers < num_qubits:
        print("Warning: Underconstrained system. 'to_circuit' works on full Tableaus.")
        # We might need to fill the rest with dummy stabilizers or Z's if they commute
        # Or use a different approach.
        # Let's try to construct a Tableau from the stabilizers we have, 
        # stim might error if they are not full rank or not max length.
        
    try:
        # Create a tableau from the stabilizers. 
        # allow_underconstrained=True might be needed if not full rank
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        print("Tableau constructed successfully.")
        
        # Method 1: Graph State
        try:
            circ_graph = t.to_circuit(method="graph_state")
            with open("candidate_graph_v4.stim", "w") as f:
                f.write(str(circ_graph))
            print("Generated candidate_graph_v4.stim using method='graph_state'")
        except Exception as e:
            print(f"Failed to generate graph state circuit: {e}")

        # Method 2: Elimination
        try:
            circ_elim = t.to_circuit(method="elimination")
            with open("candidate_elim_v4.stim", "w") as f:
                f.write(str(circ_elim))
            print("Generated candidate_elim_v4.stim using method='elimination'")
        except Exception as e:
            print(f"Failed to generate elimination circuit: {e}")
            
    except Exception as e:
        print(f"Failed to construct tableau: {e}")

if __name__ == "__main__":
    generate_candidates()
