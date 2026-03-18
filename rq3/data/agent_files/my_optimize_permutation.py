import stim
import random

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def get_metrics(circuit):
    cx_count = 0
    for op in circuit.flattened():
        if op.name == 'CX':
            cx_count += len(op.targets_copy()) // 2
    volume = len(list(circuit.flattened()))
    return cx_count, volume

def solve():
    baseline = load_circuit('current_task_baseline.stim')
    sim = stim.TableauSimulator()
    sim.do(baseline)
    # Get the state tableau (inverse of inverse)
    tableau = sim.current_inverse_tableau().inverse()
    
    n = len(tableau)
    qubits = list(range(n))
    
    # We know the baseline has 781 CX (from tool output)
    # But let's calculate it to be consistent
    base_cx, base_vol = get_metrics(baseline)
    
    best_cx = base_cx
    best_vol = base_vol
    best_circuit = baseline
    
    print(f"Original: CX={best_cx}, Vol={best_vol}")
    
    # Try 10000 permutations - we need to beat 781
    for i in range(10000):
        perm = list(qubits)
        random.shuffle(perm)
        
        # We want to synthesize the tableau T' where qubits are permuted.
        # T corresponds to state |psi>.
        # We want to synthesize |psi'> = P |psi>.
        # We can physically apply the permutation to the circuit that prepares |psi>,
        # then extract the tableau of |psi'>.
        
        # Relabel baseline: q -> perm[q]
        relabelled_baseline = stim.Circuit()
        for op in baseline.flattened():
            targets = []
            for t in op.targets_copy():
                if t.is_qubit_target:
                    targets.append(perm[t.value])
                else:
                    targets.append(t)
            relabelled_baseline.append(op.name, targets, op.gate_args_copy())
            
        # Get tableau of relabelled state
        sim_perm = stim.TableauSimulator()
        sim_perm.do(relabelled_baseline)
        t_perm = sim_perm.current_inverse_tableau().inverse()
        
        # Synthesize
        try:
            c_perm = t_perm.to_circuit(method="elimination")
            cx, vol = get_metrics(c_perm)
            
            # Optimization check
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"Found better: CX={cx}, Vol={vol} (iter {i})")
                best_cx = cx
                best_vol = vol
                
                # Un-relabel c_perm
                # We used q_new = perm[q_old].
                # So q_old = inv_perm[q_new].
                inv_perm = {v: k for k, v in enumerate(perm)}
                
                c_final = stim.Circuit()
                for op in c_perm.flattened():
                    targets = []
                    for t in op.targets_copy():
                        if t.is_qubit_target:
                            targets.append(inv_perm[t.value])
                        else:
                            targets.append(t)
                    c_final.append(op.name, targets, op.gate_args_copy())
                
                best_circuit = c_final
                with open('candidate_optimized.stim', 'w') as f:
                    f.write(str(best_circuit))
                    
        except Exception as e:
            pass

    print(f"Best found: CX={best_cx}, Vol={best_vol}")
    
    # Verify stabilizers
    print("Verifying stabilizers...")
    with open('current_task_stabilizers.txt', 'r') as f:
        lines = f.readlines()
    stabilizers = [line.strip().replace('_', 'I') for line in lines if line.strip()]
    
    sim = stim.TableauSimulator()
    sim.do(best_circuit)
    preserved = 0
    for stab in stabilizers:
        if sim.peek_observable_expectation(stim.PauliString(stab)) == 1:
            preserved += 1
    print(f"Best circuit preserves {preserved}/{len(stabilizers)} stabilizers.")

if __name__ == "__main__":
    solve()
