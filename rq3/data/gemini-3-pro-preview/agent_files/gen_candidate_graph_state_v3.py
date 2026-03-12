import stim

def main():
    # Read stabilizers
    filename = "target_stabilizers_task.txt"
    with open(filename, "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = [stim.PauliString(l) for l in lines]
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Create Tableau
    # usage of allow_underconstrained and allow_redundant to handle potential issues
    try:
        tableau = stim.Tableau.from_stabilizers(
            stabilizers, 
            allow_underconstrained=True, 
            allow_redundant=True
        )
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit
    # method='graph_state' is good for CZ optimization
    circuit = tableau.to_circuit(method="graph_state")
    
    # Post-process circuit
    # Replace RX (reset to |+>) with H (assuming start from |0>)
    # Remove R/RZ (reset to |0>) (assuming start from |0>)
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX target is a reset to X basis (|+>). 
            # From |0>, H gives |+>.
            new_circuit.append("H", instruction.targets_copy())
        elif instruction.name in ["R", "RZ"]:
            # Reset to Z basis (|0>).
            # From |0>, this is Identity.
            pass
        else:
            new_circuit.append(instruction)
            
    out_file = "candidate_graph_state_v3.stim"
    with open(out_file, "w") as f:
        f.write(str(new_circuit))
        
    print(f"Written to {out_file}")

if __name__ == "__main__":
    main()
