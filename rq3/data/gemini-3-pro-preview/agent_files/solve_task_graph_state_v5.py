import stim

target_stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI", "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX", "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ", "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ", "XXXXXXXXXXIIIIIIIIIIXXXXXXXXXXIIIII", "XXXXXIIIIIXXXXXIIIIIXXXXXIIIIIXXXXX", "IIIIIIIIIIIIIIIXXXXXXXXXXXXXXXXXXXX", "ZZZZZZZZZZIIIIIIIIIIZZZZZZZZZZIIIII", "ZZZZZIIIIIZZZZZIIIIIZZZZZIIIIIZZZZZ", "IIIIIIIIIIIIIIIZZZZZZZZZZZZZZZZZZZZ"
]

# Create a Tableau from the stabilizers
try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in target_stabilizers], allow_underconstrained=True)
    
    # Synthesize the circuit using graph state method
    circuit = tableau.to_circuit(method="graph_state")
    
    # Post-process: Replace RX with H if we assume input is |0>
    # Also remove MPP if any, though graph_state usually uses standard gates
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX target is a reset to X basis (|+>). H on |0> gives |+>.
            # If the circuit starts from scratch (which it usually does implicitly in these tasks),
            # this is a valid replacement for the initialization.
            for t in instruction.targets_copy():
                new_circuit.append("H", [t])
        elif instruction.name == "R" or instruction.name == "RZ":
             # Reset to Z basis (|0>). If we assume start at |0>, this is a no-op or identity.
             # But let's keep it if it's explicit reset, or remove if it's at start.
             # Actually, standard graph state synthesis puts resets at the beginning.
             # If we just want a unitary that PREPARES the state from |0>, we can drop initial R/RZ.
             pass
        else:
            new_circuit.append(instruction)
            
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))
    print("Candidate written to candidate.stim")

except Exception as e:
    print(f"Error: {e}")
