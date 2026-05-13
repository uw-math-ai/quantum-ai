import stim
import collections

def analyze_coverage(circuit_path, stabs_path):
    with open(circuit_path, 'r') as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    num_qubits = max(circuit.num_qubits, 81)
    ops = list(circuit)
    
    with open(stabs_path, 'r') as f:
        stabs_str = [line.strip() for line in f if line.strip()]
    
    # Parse stabilizers
    stabilizers = []
    for s in stabs_str:
        ps = stim.PauliString(s)
        stabilizers.append(ps)
        
    print(f"Tracking {len(stabilizers)} stabilizers...")
    print(f"Circuit has {num_qubits} qubits.")
    if len(stabilizers) > 0:
        print(f"First stabilizer length: {len(stabilizers[0])}")
    
    # Track stabilizers backwards
    # map: op_index -> list of stabilizers at that point (after op)
    stabs_at_step = {}
    
    # Initially (at end), stabs are the targets
    current_stabs = [s for s in stabilizers]
    stabs_at_step[len(ops)] = current_stabs # after last op
    
    for i in range(len(ops) - 1, -1, -1):
        op = ops[i]
        
        # Evolve stabs backwards through op
        # S_prev = op_dagger * S_curr * op
        # stim.Tableau(op).inverse()(S_curr)?
        # Or just conjugate.
        # Since op is unitary and mostly self-inverse (CX, H, SWAP, Z, X). S is not self-inverse (Phase).
        # But here we have CX, H. Self-inverse?
        # CX is self-inverse. H is self-inverse.
        # So S_prev = op * S_curr * op.
        # We can use Tableau to conjugate.
        
        op_circuit = stim.Circuit()
        op_circuit.append("I", [num_qubits - 1])
        op_circuit.append(op)
        op_tableau = stim.Tableau.from_circuit(op_circuit)
        
        # Conjugate PauliStrings
        # T(P) = U P U^dagger.
        # Here we want U^dagger P U ?
        # If we go backwards, S_{in} maps to S_{out} via U.
        # S_{out} = U S_{in} U^dagger.
        # S_{in} = U^dagger S_{out} U.
        # For CX and H, U = U^dagger.
        # So S_{in} = U S_{out} U^dagger = T(S_{out}).
        # So we just apply the tableau to the stabilizers.
        
        new_stabs = []
        for s in current_stabs:
            new_stabs.append(op_tableau(s))
            
        current_stabs = new_stabs
        stabs_at_step[i] = current_stabs # Stabs AFTER op i (wait. this is BEFORE op i? No.)
        # loop index i is the op we just reversed.
        # So current_stabs is now the state BEFORE op i.
        # Which is state AFTER op i-1.
        # So stabs_at_step[i] = current_stabs
        
        # Wait, key mapping:
        # ops[i] is the instruction at index i.
        # stabs_at_step[i] should be stabs available AFTER ops[i-1] and BEFORE ops[i].
        # Let's say:
        # stabs_at_step[0] = initial stabs (before any op)
        # stabs_at_step[i] = stabs before op i.
        # stabs_at_step[len(ops)] = final stabs.
        
        # In loop, we process op[i].
        # We start with stabs AFTER op[i] (which is stabs_at_step[i+1]).
        # We compute stabs BEFORE op[i] (which is stabs_at_step[i]).
        pass
        
    # Re-run bad fault analysis and check coverage
    bad_faults = []
    
    # We can reuse the bad_faults.txt if we trust it, or re-run.
    # Let's re-run to be self-contained.
    
    current_tableau = stim.Tableau(num_qubits)
    
    needed_checks = collections.defaultdict(list) # op_index -> list of stabilizers to measure
    
    print("Analyzing faults...")
    
    for i in range(len(ops) - 1, -1, -1):
        op = ops[i]
        
        targets = []
        for t in op.targets_copy():
            if t.is_qubit_target:
                targets.append(t.value)
        
        # These faults occur AFTER op[i].
        # So we check against stabs available AFTER op[i].
        # i.e. stabs_at_step[i+1].
        
        # But wait. current_stabs inside the loop above were evolving backwards.
        # Let's correct the loop above.
        
        # Forward pass might be easier for fault analysis?
        # But previous script used backwards.
        pass

    # Actually, let's just use the `bad_faults.txt` or re-compute.
    # Re-computing is safer.
    
    # We need to map loop index to stabs.
    # stabs_at_step[k] = stabs valid between op[k-1] and op[k].
    # Faults at op_index i are AFTER op[i].
    # So we need stabs_at_step[i+1].
    
    # Let's populate stabs_at_step correctly.
    stabs_map = {}
    curr = [s for s in stabilizers]
    stabs_map[len(ops)] = curr
    
    for i in range(len(ops) - 1, -1, -1):
        op = ops[i]
        op_circuit = stim.Circuit()
        op_circuit.append("I", [num_qubits - 1])
        op_circuit.append(op)
        op_tableau = stim.Tableau.from_circuit(op_circuit)
        
        next_s = []
        for s in curr:
            next_s.append(op_tableau(s))
        curr = next_s
        stabs_map[i] = curr
        
    # Now analyze faults
    current_tableau = stim.Tableau(num_qubits)
    
    uncovered_faults = 0
    covered_faults = 0
    
    # We want to select minimal set of checks.
    # Ideally, one check per "layer" that covers all faults in that layer?
    # Or insert checks only where needed.
    
    proposed_checks = []
    
    for i in range(len(ops) - 1, -1, -1):
        op = ops[i]
        
        # Faults after op i
        active_stabs = stabs_map[i+1]
        
        targets = []
        for t in op.targets_copy():
            if t.is_qubit_target:
                targets.append(t.value)
        
        for q in targets:
            for p_name in ["X", "Y", "Z"]:
                # 1. Compute weight
                x_out = current_tableau.x_output(q)
                z_out = current_tableau.z_output(q)
                
                final_pauli = None
                if p_name == "X": final_pauli = x_out
                elif p_name == "Z": final_pauli = z_out
                elif p_name == "Y": final_pauli = x_out * z_out
                
                w = 0
                s_str = str(final_pauli)
                for k in range(81):
                    if k+1 < len(s_str) and s_str[k+1] != '_':
                        w += 1
                
                if w >= 4:
                    # Bad fault. Check if covered.
                    # Fault is Pauli P on qubit q.
                    # Does it anti-commute with any active stab?
                    # P is a single qubit error here (at step i).
                    # Active stab S is a Pauli string.
                    # Check commutation of P and S on qubit q.
                    # P commutes with S if P_q and S_q commute.
                    
                    covered = False
                    best_s_idx = -1
                    
                    # Heuristic: Pick lowest weight stabilizer that covers it?
                    # Or just any.
                    
                    for idx, s in enumerate(active_stabs):
                        # check anti-commutation on qubit q
                        # s[q] gives the pauli at q (0=I, 1=X, 2=Y, 3=Z)
                        # p_name to int: X=1, Y=2, Z=3
                        
                        # Wait, Stim PauliString access?
                        # s[q] returns int?
                        # No, Stim PauliString might not support indexing like that directly in old versions?
                        # 1.15.0 supports indexing.
                        # Returns 0,1,2,3.
                        
                        s_p = s[q] # 0=I, 1=X, 2=Y, 3=Z
                        f_p = 0
                        if p_name == 'X': f_p = 1
                        elif p_name == 'Y': f_p = 2
                        elif p_name == 'Z': f_p = 3
                        
                        # Commute if s_p == 0 or f_p == 0 or s_p == f_p.
                        # Anti-commute if distinct and non-zero.
                        if s_p != 0 and f_p != 0 and s_p != f_p:
                            covered = True
                            best_s_idx = idx
                            break
                    
                    if covered:
                        covered_faults += 1
                        # Record that we need to measure stabilizer best_s_idx at step i+1
                        proposed_checks.append((i+1, best_s_idx))
                    else:
                        uncovered_faults += 1
                        # print(f"Uncovered: {i}, {q}, {p_name}, w={w}")

        # Update tableau
        op_circuit = stim.Circuit()
        op_circuit.append("I", [num_qubits - 1])
        op_circuit.append(op)
        op_tableau = stim.Tableau.from_circuit(op_circuit)
        current_tableau = current_tableau.then(op_tableau)

    print(f"Covered: {covered_faults}, Uncovered: {uncovered_faults}")
    
    # Process proposed checks
    # Map step -> set of stabs
    checks_map = collections.defaultdict(set)
    for step, s_idx in proposed_checks:
        checks_map[step].add(s_idx)
        
    print(f"Proposed {len(checks_map)} check locations.")
    for step in sorted(checks_map.keys()):
        print(f"Step {step}: Measure {list(checks_map[step])}")

    # Save checks to file for generation script
    with open("checks.txt", "w") as f:
        for step in sorted(checks_map.keys()):
            s_idxs = list(checks_map[step])
            f.write(f"{step}:{','.join(map(str, s_idxs))}\n")

if __name__ == "__main__":
    analyze_coverage("input.stim", "stabilizers.txt")
