import stim
import itertools

def generate_single_qubit_lookup():
    # Gates to use for synthesis
    gates = ["I", "H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]
    
    # BFS to find shortest sequence for each tableau
    lookup = {} # tableau_hash -> circuit string
    
    # Depth 0
    t0 = stim.Circuit().to_tableau()
    lookup[str(t0)] = stim.Circuit()
    
    # Depth 1
    for g in gates:
        c = stim.Circuit(f"{g} 0")
        t = c.to_tableau()
        if str(t) not in lookup:
            lookup[str(t)] = c
            
    # Depth 2
    for g1 in gates:
        for g2 in gates:
            c = stim.Circuit(f"{g1} 0\n{g2} 0")
            t = c.to_tableau()
            if str(t) not in lookup:
                lookup[str(t)] = c

    # Depth 3 (Cliffords need at most 3? XYZ group is 24 size. H, S generate it. H, S, H S H...)
    # Actually, standard gates might need 3. E.g. H S H.
    for g1 in gates:
        for g2 in gates:
            for g3 in gates:
                c = stim.Circuit(f"{g1} 0\n{g2} 0\n{g3} 0")
                t = c.to_tableau()
                if str(t) not in lookup:
                    lookup[str(t)] = c
                    
    print(f"Generated lookup table with {len(lookup)} entries.")
    return lookup

lookup = generate_single_qubit_lookup()

def get_optimized_sequence(tableau):
    h = str(tableau)
    if h in lookup:
        return lookup[h]
    # Fallback (should cover all 24 cliffords, but just in case)
    return tableau.to_circuit("elimination")

# Load baseline
with open("baseline.stim") as f:
    baseline = stim.Circuit(f.read())

new_circuit = stim.Circuit()
pending_tableaus = {} # qubit -> stim.Tableau (single qubit)

def flush(q):
    if q not in pending_tableaus:
        return
    t = pending_tableaus[q]
    # Find optimized gates
    c = get_optimized_sequence(t)
    # Append to new_circuit
    for op in c:
        new_circuit.append(op.name, [q])
    del pending_tableaus[q]

def update_pending(q, op_name):
    if q not in pending_tableaus:
        pending_tableaus[q] = stim.Tableau(1)
    
    # Apply op to the pending tableau
    # T_new = T_op * T_old
    # We can do this by converting pending to circuit, appending op, then to tableau
    # Efficient enough for 1 qubit
    # Note: we need to handle the gate name
    c = stim.Circuit()
    # We need to reconstruct the tableau operation
    # Ideally we'd compose tableaus. stim.Tableau.then() does T_new = T_old.then(T_op) -> T_op(T_old)
    # Yes.
    
    # Create tableau for the op
    op_c = stim.Circuit(f"{op_name} 0")
    op_t = op_c.to_tableau()
    
    pending_tableaus[q] = pending_tableaus[q].then(op_t)

# Iterate instructions
for op in baseline:
    if op.name in ["CX", "CZ", "SWAP"]: # 2-qubit gates
        targets = op.targets_copy()
        for t in targets:
            flush(t.value)
        new_circuit.append(op)
    elif op.name in ["M", "R", "RX", "RY", "RZ", "MPP"]: # Operations that break commutation/fusion or resets
        targets = op.targets_copy()
        for t in targets:
            flush(t.value)
        new_circuit.append(op)
    else:
        # Assumed 1-qubit gate (H, S, X, Y, Z, etc)
        targets = op.targets_copy()
        for t in targets:
            update_pending(t.value, op.name)

# Flush remaining
qubits = list(pending_tableaus.keys())
for q in qubits:
    flush(q)

with open("candidate_optimized_sq.stim", "w") as f:
    f.write(str(new_circuit))

print("Candidate saved to candidate_optimized_sq.stim")
cx = new_circuit.num_2_qubit_gates() if hasattr(new_circuit, "num_2_qubit_gates") else -1
print(f"New circuit size: {len(new_circuit)}")
