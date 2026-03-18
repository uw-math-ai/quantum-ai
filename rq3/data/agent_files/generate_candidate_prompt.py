import stim

def generate_candidate_prompt():
    # Load prompt stabilizers
    with open("target_stabilizers_prompt.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Loaded {len(lines)} stabilizers.")
    
    # Create tableau from stabilizers
    # Note: we should verify if the text length matches the number of qubits we want.
    # The text length is 119.
    # The baseline has 133 qubits.
    # If we synthesize for 119, we might miss constraints on 119..132?
    # But if the prompt only lists 119, then 119..132 are unconstrained.
    # So we can synthesize for 119, and then extend the circuit to 133?
    # Or just let stim handle it (if we add identity on 132).
    
    # But wait, to extend to 133, we need to declare 133 qubits?
    # Stim circuit doesn't need explicit declaration if we use high indices.
    # But graph state synthesis on 119 will use 0..118.
    # We can add `I 132` at the end to force 133 qubits.
    
    stabilizers = [stim.PauliString(l) for l in lines]
    
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit
    # Using graph_state method
    circuit = tableau.to_circuit("graph_state")
    
    # Check qubit count
    print(f"Synthesized circuit has {circuit.num_qubits} qubits.")
    
    # Add dummy operation to force 133 qubits if needed
    if circuit.num_qubits < 133:
        circuit.append("I", [132])
        
    print(f"Final circuit has {circuit.num_qubits} qubits.")
    
    with open("candidate_prompt.stim", "w") as f:
        f.write(str(circuit))
        
    print("Candidate generated in candidate_prompt.stim")

if __name__ == "__main__":
    generate_candidate_prompt()
