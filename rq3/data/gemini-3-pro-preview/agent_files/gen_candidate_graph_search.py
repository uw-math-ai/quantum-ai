import stim

target_stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI", "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX", "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ", "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ", "XXXXXXXXXXIIIIIIIIIIXXXXXXXXXXIIIII", "XXXXXIIIIIXXXXXIIIIIXXXXXIIIIIXXXXX", "IIIIIIIIIIIIIIIXXXXXXXXXXXXXXXXXXXX", "ZZZZZZZZZZIIIIIIIIIIZZZZZZZZZZIIIII", "ZZZZZIIIIIZZZZZIIIIIZZZZZIIIIIZZZZZ", "IIIIIIIIIIIIIIIZZZZZZZZZZZZZZZZZZZZ"
]

best_cz = 999999
best_circ = None

for i in range(20):
    try:
        # We re-create tableau each time just in case
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in target_stabilizers], allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        # Count CZs
        cz_count = 0
        for instr in circuit:
            if instr.name == "CZ":
                cz_count += len(instr.targets_copy()) // 2
        
        if cz_count < best_cz:
            best_cz = cz_count
            best_circ = circuit
            print(f"Iter {i}: Found better CZ count: {cz_count}. Num qubits: {circuit.num_qubits}")
            
    except Exception as e:
        print(f"Iter {i}: Error {e}")

# Save best
if best_circ:
    # Post process RX -> H
    new_circuit = stim.Circuit()
    for instruction in best_circ:
        if instruction.name == "RX":
            for t in instruction.targets_copy():
                new_circuit.append("H", [t])
        elif instruction.name in ["R", "RZ"]:
             pass
        else:
            new_circuit.append(instruction)
            
    with open("candidate_search.stim", "w") as f:
        f.write(str(new_circuit))
    print("Saved candidate_search.stim")
