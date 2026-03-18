import stim

def try_graph_state():
    # Load stabilizers
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    # Try with allow_underconstrained=True
    tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
    
    # Synthesize with graph_state
    try:
        circuit = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Graph state synthesis failed: {e}")
        return

    # Analyze circuit
    cz_count = 0
    rx_count = 0
    other_count = 0
    
    new_circuit = stim.Circuit()
    
    for instr in circuit:
        if instr.name == "CZ":
            cz_count += len(instr.targets_copy()) // 2
            new_circuit.append(instr)
        elif instr.name == "RX":
            rx_count += len(instr.targets_copy())
            # Replace RX with H (assuming input |0>)
            # RX resets to |+>. H|0> -> |+>.
            new_circuit.append("H", instr.targets_copy())
        else:
            other_count += 1
            new_circuit.append(instr)
            
    print(f"Graph state circuit has {cz_count} CZ gates, {rx_count} RX gates.")
    
    # If we convert CZ to CX:
    # CZ(c, t) = H(t) CX(c, t) H(t)
    # So 1 CZ -> 1 CX.
    # Total CX = cz_count.
    
    print(f"Equivalent CX count: {cz_count}")
    
    # Verify preservation
    sim = stim.TableauSimulator()
    sim.do(new_circuit)
    preserved = 0
    for p in paulis:
        if sim.peek_observable_expectation(p) == 1:
            preserved += 1
            
    print(f"Graph state circuit preserves {preserved}/{len(paulis)} stabilizers.")
    
    if preserved == len(paulis):
        new_circuit.to_file("candidate_graph.stim")
        print("Saved valid graph state candidate.")

if __name__ == "__main__":
    try_graph_state()
