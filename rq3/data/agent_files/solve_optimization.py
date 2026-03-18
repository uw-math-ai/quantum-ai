import stim

def solve():
    print("Loading stabilizers...")
    with open("current_target_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Check lines for length
    if not lines:
        print("Error: No stabilizers found.")
        return

    # Create tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in lines], allow_underconstrained=True)
        print(f"Tableau created. Size: {len(t)}")
        print(f"Number of stabilizers: {len(lines)}")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize graph state circuit
    print("Synthesizing graph state circuit...")
    # method="graph_state" might fail for underconstrained? 
    # Let's try "elimination" as fallback if graph_state fails or isn't supported for this.
    # Actually, graph_state decomposition works for any stabilizer state.
    # If underconstrained, it picks a state.
    
    try:
        c_graph = t.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Graph state synthesis failed: {e}")
        print("Falling back to elimination...")
        c_graph = t.to_circuit(method="elimination")
        
    # Analyze generated circuit
    ops = list(c_graph)
    has_cx = any(op.name == "CX" or op.name == "CNOT" for op in ops)
    has_cz = any(op.name == "CZ" for op in ops)
    has_rx = any(op.name == "RX" for op in ops)
    
    print(f"Generated circuit has CX: {has_cx}")
    print(f"Generated circuit has CZ: {has_cz}")
    print(f"Generated circuit has RX: {has_rx}")
    
    # Process RX -> H
    if has_rx:
        print("Replacing RX with H...")
        new_circuit = stim.Circuit()
        for op in c_graph:
            if op.name == "RX":
                # RX target -> H target
                new_circuit.append("H", op.targets_copy())
            else:
                new_circuit.append(op)
        c_graph = new_circuit
            
    # Save raw candidate
    with open("candidate_graph.stim", "w") as f:
        f.write(str(c_graph))
    print("Candidate saved to candidate_graph.stim")


if __name__ == "__main__":
    solve()
