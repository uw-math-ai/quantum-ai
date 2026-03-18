import stim
import random

# Target stabilizers
stabilizers = [
    "IIXIXXX", "IXIXIXX", "XXXIIXI",
    "IIZIZZZ", "IZIZIZZ", "ZZZIIZI"
]
t_target = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)

# Helper to count volume
def get_volume(circ):
    vol = 0
    for op in circ:
        if op.name in ["TICK", "SHIFT_COORDS", "QUBIT_COORDS"]:
            continue
        # For each target in the instruction
        n_targets = len(op.targets_copy())
        # Gates like CX a b c d have 2 pairs, so 2 gates?
        # Stim circuit op has targets. CX 0 1 2 3 is 2 CX gates.
        if op.name in ["CX", "CY", "CZ", "SWAP", "ISWAP"]:
            vol += n_targets // 2
        else:
            vol += n_targets
    return vol

# Helper to get CX count
def get_cx(circ):
    cx = 0
    for op in circ:
        if op.name == "CX":
            cx += len(op.targets_copy()) // 2
    return cx

best_circ = None
best_vol = 999
best_cx = 999

# Try 1000 random LC frames
print("Searching...")
for i in range(200):
    # Construct random single-qubit Clifford layer
    # We'll represent it as a circuit of H, S
    cliff_layer = stim.Circuit()
    inv_cliff_layer = stim.Circuit()
    
    # Randomly pick H, S, HS, SH, HSH, S S ...
    # Simplified: Randomly apply H, S.
    # Actually, iterate over qubits
    for q in range(7):
        # 0: I, 1: H, 2: S, 3: HS, 4: SH, 5: HSH (Z->Y? No)
        # Just pick from [I, H, S, H S, S H, H S H]
        r = random.randint(0, 5)
        if r == 0: pass
        elif r == 1: 
            cliff_layer.append("H", [q])
            inv_cliff_layer.append("H", [q]) # H inv is H
        elif r == 2:
            cliff_layer.append("S", [q])
            inv_cliff_layer.append("S_DAG", [q])
        elif r == 3: # HS (apply S then H? No, appended in order. H then S)
            cliff_layer.append("H", [q])
            cliff_layer.append("S", [q])
            # Inv: S_DAG then H
            inv_cliff_layer.append("S_DAG", [q]) # Prepend? No, circuit order.
            # We want (HS)^dag = S^dag H^dag = S_dag H
            # If we append to inv_layer: we want it to apply AFTER the main circuit.
            # So if we apply C, then Circuit, then C_inv.
            # inv_cliff_layer should apply S_DAG then H.
            # But wait, we are building inv_cliff_layer from scratch for each qubit.
            # We need to collect them.
            pass
    
    # Correct logic:
    # We want T' = U T. U is local cliffords.
    # Then Circ' implements T'.
    # Then Total = U_inv Circ'.  Wait.
    # If Circ' stabilizes T', i.e. Circ' |0> = |psi'>.
    # And |psi'> = U |psi>.
    # So |psi> = U_inv |psi'> = U_inv Circ' |0>.
    # So we apply Circ' then U_inv.
    
    # Let's generate U and U_inv
    u = stim.Circuit()
    u_inv = stim.Circuit()
    
    for q in range(7):
        # Pick a random unitary from {I, H, S, H S, S H, H S H}
        # S H means S(H(q))
        ops = []
        r = random.randint(0, 5)
        if r == 0: ops = []
        elif r == 1: ops = ["H"]
        elif r == 2: ops = ["S"]
        elif r == 3: ops = ["H", "S"] # H then S
        elif r == 4: ops = ["S", "H"]
        elif r == 5: ops = ["H", "S", "H"]
        
        for op in ops:
            u.append(op, [q])
            
        # Inverse ops in reverse order
        for op in reversed(ops):
            if op == "S":
                u_inv.append("S_DAG", [q])
            else:
                u_inv.append(op, [q])
                
    # Apply U to tableau
    # Stim Tableau doesn't support applying a circuit directly efficiently without simulation?
    # Actually `stim.Tableau.from_circuit(u).then(t_target)`?
    # No, we want T_new = U * T_target * U_dag ?
    # Stabilizers S -> U S U_dag.
    # Yes.
    
    # We can assume the synthesized circuit C_new prepares state stabilized by U S U_dag.
    # So C_new |0> = U |psi>.
    # So U_inv C_new |0> = |psi>.
    # So candidate is U_inv + C_new.
    # Wait, order: C_new is first (from |0>), then U_inv.
    
    # Construct T_new
    # We can do this by converting t_target to circuit, appending U, converting back to tableau
    # (Slow but fine for 7 qubits)
    # Actually, t_target doesn't convert to circuit easily if it's not graph state.
    # But we can just assume `to_circuit(method="graph_state")` works on t_target.
    # Let's just use `to_circuit` on t_target first to get a base circuit.
    
    base_circ = t_target.to_circuit(method="graph_state")
    # This prepares |psi>.
    # We want a circuit for U |psi>.
    # That is `base_circ + u`.
    # Let's verify: (base_circ + u) |0> = u (base_circ |0>) = u |psi>.
    # So `(base_circ + u).to_tableau()` gives T_new.
    
    t_new = (base_circ + u).to_tableau()
    
    # Synthesize T_new
    c_syn = t_new.to_circuit(method="graph_state")
    
    # Full candidate: c_syn + u_inv
    cand = c_syn + u_inv
    
    # Simplify (fuse gates)
    # Stim doesn't have internal fuse optimization exposed easily?
    # We can write a quick fuse pass or trust `stim.Circuit` doesn't fuse?
    # Stim DOES NOT auto fuse.
    # But we can check metrics.
    # If we have H followed by H, it's I.
    # If we have S followed by S_DAG, it's I.
    
    # For now, just count raw. If it's low, we can optimize.
    # But `c_syn` usually ends with single qubit gates. `u_inv` is single qubit gates.
    # They can be merged.
    # c_syn: Init + CZ + Final_Singles
    # u_inv: Singles
    # Total: Init + CZ + (Final_Singles + Singles)
    # The cost is Init + CZ + merged(Final+Inv).
    # Init is usually H or RX. (7 gates)
    # CZ count is the main variable.
    # Final layer size is the other variable.
    
    # Let's just count CZs first.
    cz_count = 0
    for op in c_syn:
        if op.name == "CZ":
            cz_count += len(op.targets_copy()) // 2
            
    # Estimate volume
    # Init (7) + CZ (cz_count) + Final?
    # We need to know the final layer size.
    # We can simulate the merging.
    # Or just count gates in c_syn and u_inv and subtract cancellations?
    # That's hard.
    
    # Alternative:
    # Just look for low CZ count (< 9).
    # If CZ < 9, it's a win on volume probably (unless final layer is huge).
    
    if cz_count < 9:
        print(f"Found better CZ count: {cz_count}")
        # Build full circuit and print
        full = c_syn + u_inv
        # We should fuse it to see true volume
        # But for now, just save it.
        # Check volume
        vol = get_volume(full)
        print(f"Raw Volume: {vol} (ignoring fusion)")
        if cz_count == 0:
             # Just in case
             pass
    
    # Also check if cz=9 but volume is better than 20.
    # Current best is 20.
    # c_syn + u_inv might be messy.
    
print("Done.")
