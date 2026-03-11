import stim

stabilizers = [
"IIXIIXIIIIIIIIIIIIIIIIIIIXIIXII",
"IIIIIIIIIIXIIXIIIIIIIXIIIIIXIII",
"IIIIIIIIIIIIXIIXIIIIIIIXIIIIIIX",
"IXIIXIIIIIIIIIIIIIIIIIIIXIXIIII",
"IIIIIIXXIIIIIIXIXIIIIIIIIIIIIII",
"IIIIIIIIXXIIIIIIIIXIXIIIIIIIIII",
"IIIIIIIIIIIIIIIIIIIXIIXIIXIIXII",
"IIIXIIIIIIXXIXIIIIIIIIIIIIIIIII",
"IIIIXIIIIIIIIIIIIIIIIXIIIIXXIII",
"IIIIIXXIIIIIXIIXXIIIIIXIIIIIXXI",
"IIIIIIIIXIIIIIIIIIXIIIIXIIIIIIX",
"XIIXIIIXIIXIIIXIIIIIIXIIXIXIIII",
"XIIIIIXXIIIIIIIIIIIIIIIIIIIIIXI",
"IXIIIIIIXXIIIIXXXIIIIIIIXIIIIIX",
"IIXIIIIIIIIIIIIIIXIXIIIIIXIIIII",
"IIZIIZIIIIIIIIIIIIIIIIIIIZIIZII",
"IIIIIIIIIIZIIZIIIIIIIZIIIIIZIII",
"IIIIIIIIIIIIZIIZIIIIIIIZIIIIIIZ",
"IZIIZIIIIIIIIIIIIIIIIIIIZIZIIII",
"IIIIIIZZIIIIIIZIZIIIIIIIIIIIIII",
"IIIIIIIIZZIIIIIIIIZIZIIIIIIIIII",
"IIIIIIIIIIIIIIIIIIIZIIZIIZIIZII",
"IIIZIIIIIIZZIZIIIIIIIIIIIIIIIII",
"IIIIZIIIIIIIIIIIIIIIIZIIIIZZIII",
"IIIIIZZIIIIIZIIZZIIIIIZIIIIIZZI",
"IIIIIIIIZIIIIIIIIIZIIIIZIIIIIIZ",
"ZIIZIIIZIIZIIIZIIIIIIZIIZIZIIII",
"ZIIIIIZZIIIIIIIIIIIIIIIIIIIIIZI",
"IZIIIIIIZZIIIIZZZIIIIIIIZIIIIIZ",
"IIZIIIIIIIIIIIIIIZIZIIIIIZIIIII"
]

# Fix the missing quote in the list above
stabilizers[18] = "IZIIZIIIIIIIIIIIIIIIIIIIZIZIIII"

try:
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    circ = t.to_circuit(method="graph_state")
    
    # Stim's graph state synthesis often includes resetting qubits or other operations.
    # The prompt says "Do NOT introduce measurements, resets, or noise unless they already exist".
    # The baseline has no resets (implied).
    # If `circ` has resets (RX, RY, RZ), we must remove them if possible.
    # Usually `to_circuit` starts with resets if it thinks the state is mixed, but here we have a pure state (mostly).
    # Or it assumes we start from arbitrary state?
    # No, `to_circuit` generates a unitary U such that U|0> = state.
    # But sometimes it uses resets. Let's check.
    
    # Post-process to replace RX with H and remove TICK
    clean_circ = stim.Circuit()
    for op in circ:
        if op.name == "RX":
            # RX is Reset X. In circuit starting at |0>, this is H.
            clean_circ.append("H", op.targets_copy())
        elif op.name == "TICK":
            continue
        else:
            clean_circ.append(op)
            
    with open("candidate.stim", "w") as f:
        print(clean_circ, file=f)
        
    print("Written to candidate.stim")

except Exception as e:
    print(f"Error: {e}")
