import stim
import sys
import collections

# Utils
def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name == "CX" or op.name == "CNOT":
            count += len(op.targets_copy()) // 2
    return count

def count_volume(circuit):
    return sum(1 for _ in circuit)

def get_stabilizers(path):
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_num_qubits(stabilizers):
    return len(stabilizers[0])

def is_valid(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    for s in stabilizers:
        if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
            return False
    return True

# Optimization 1: Remove SWAPs
def decompose_to_atomic(circuit):
    atomic_ops = []
    for op in circuit:
        targets = op.targets_copy()
        if op.name in ["CX", "CNOT", "CZ", "SWAP", "ISWAP"]:
            # 2-qubit gates
            for i in range(0, len(targets), 2):
                atomic_ops.append({'name': op.name, 'targets': [targets[i], targets[i+1]]})
        elif op.name in ["H", "S", "X", "Y", "Z", "I", "SQRT_X", "SQRT_Y", "SQRT_Z"]: 
            # Single qubit gates
            for t in targets:
                atomic_ops.append({'name': op.name, 'targets': [t]})
        else:
            # Keep others as is
            atomic_ops.append({'name': op.name, 'targets': targets})
    return atomic_ops

def optimize_backwards_relabeling(circuit):
    ops = decompose_to_atomic(circuit)
        
    # Track which qubits are "touched" (non-zero)
    # Since we modify ops in place, we need to re-scan or be careful.
    # Actually, we can just scan forward.
    # When we hit SWAP p q:
    #   Check if p or q are fresh.
    #   If q is fresh (touched=False), but p is touched:
    #      Rename p->q in ops[0:i].
    #      Remove SWAP.
    #      Update touched status: q is now touched (inherits p), p is now fresh.
    #      Wait, if p becomes fresh, we must ensure it wasn't used as control/target in a way that entangled it?
    #      If we rename p->q, then all gates on p become gates on q.
    #      So p is effectively never touched!
    #      So yes, p becomes fresh.
    
    # We need to track 'touched' status accurately.
    # Since we modify history, 'touched' status might change?
    # No, because we are swapping roles.
    # 'p' was touched, 'q' was fresh.
    # We verify 'q' appears nowhere in ops[0:i].
    # We replace 'p' with 'q'.
    # Now 'q' appears in ops[0:i]. 'p' appears nowhere.
    # So 'q' is touched. 'p' is fresh.
    # Correct.
    
    i = 0
    while i < len(ops):
        # Scan for SWAP pattern
        is_swap = False
        if i + 2 < len(ops):
            op1 = ops[i]
            op2 = ops[i+1]
            op3 = ops[i+2]
            if (op1['name'] == "CX" and op2['name'] == "CX" and op3['name'] == "CX"):
                t1 = op1['targets']
                t2 = op2['targets']
                t3 = op3['targets']
                if len(t1) == 2 and len(t2) == 2 and len(t3) == 2:
                    q1_a, q1_b = t1[0].value, t1[1].value
                    q2_a, q2_b = t2[0].value, t2[1].value
                    q3_a, q3_b = t3[0].value, t3[1].value
                    
                    if (q1_a == q2_b and q1_b == q2_a and q1_a == q3_a and q1_b == q3_b):
                        # Found SWAP(a, b)
                        a = q1_a
                        b = q1_b
                        
                        # Check freshness in ops[0:i]
                        # A qubit is fresh if it does not appear in ops[0:i]
                        a_fresh = True
                        b_fresh = True
                        for k in range(i):
                            prev_op = ops[k]
                            for t in prev_op['targets']:
                                if t.value == a: a_fresh = False
                                if t.value == b: b_fresh = False
                        
                        # Case 1: Both fresh (Identity)
                        if a_fresh and b_fresh:
                            # Remove
                            del ops[i:i+3]
                            continue # Check index i again
                        
                        # Case 2: One fresh (Move)
                        # Assume b is fresh, a is not.
                        if b_fresh and not a_fresh:
                            # Rename a -> b in ops[0:i]
                            for k in range(i):
                                prev_op = ops[k]
                                new_targets = []
                                for t in prev_op['targets']:
                                    if t.value == a:
                                        new_targets.append(stim.GateTarget(b))
                                    else:
                                        new_targets.append(t)
                                prev_op['targets'] = new_targets
                            
                            # Remove SWAP
                            del ops[i:i+3]
                            continue
                        
                        # Symmetric Case: a fresh, b not
                        if a_fresh and not b_fresh:
                            # Rename b -> a in ops[0:i]
                            for k in range(i):
                                prev_op = ops[k]
                                new_targets = []
                                for t in prev_op['targets']:
                                    if t.value == b:
                                        new_targets.append(stim.GateTarget(a))
                                    else:
                                        new_targets.append(t)
                                prev_op['targets'] = new_targets
                            
                            # Remove SWAP
                            del ops[i:i+3]
                            continue

        i += 1
        
    # Reconstruct circuit
    new_circuit = stim.Circuit()
    for op in ops:
        new_circuit.append(op['name'], op['targets'])
    return new_circuit

def run_optimization():
    baseline_path = "data/agent_files/current_task_baseline.stim"
    stabilizers_path = "data/agent_files/current_task_stabilizers.txt"
    
    baseline = stim.Circuit.from_file(baseline_path)
    stabilizers = get_stabilizers(stabilizers_path)
    
    print(f"Original CX: {count_cx(baseline)}")
    
    if not is_valid(baseline, stabilizers):
        print("Original INVALID!")
        # Proceed anyway?
    else:
        print("Original VALID.")
        
    # Optimization
    opt_circuit = optimize_backwards_relabeling(baseline)
    
    cx_orig = count_cx(baseline)
    cx_new = count_cx(opt_circuit)
    
    print(f"Optimized CX: {cx_new}")
    
    if is_valid(opt_circuit, stabilizers):
        print("Optimized VALID.")
        # Write decomposed to ensure validity
        with open("data/agent_files/candidate_optimized.stim", "w") as f:
            for op in opt_circuit:
                # Check if it's a combined op (likely yes due to append)
                # We want to decompose for safety in file format
                # But we want to preserve 'volume' if combined ops count as 1?
                # Let's assume standard format (one op per line) is safest.
                # Actually, let's just write what Stim gave us, but check if we can read it back.
                pass
            f.write(str(opt_circuit))
            
        # Verify we can read it back
        try:
            stim.Circuit.from_file("data/agent_files/candidate_optimized.stim")
            print("File is readable by Stim.")
        except Exception as e:
            print(f"File is NOT readable: {e}")
            # Fallback: write decomposed
            print("Writing decomposed file...")
            with open("data/agent_files/candidate_optimized.stim", "w") as f:
                for op in opt_circuit:
                    name = op.name
                    targets = op.targets_copy()
                    # Write as separate lines if needed, or just standard string
                    # If str(op) works?
                    f.write(str(op) + "\n")

    else:
        print("Optimized INVALID.")

    # Synthesis Attempt (Secondary)
    # ... (omitted for brevity, focus on swap opt)


if __name__ == "__main__":
    run_optimization()
