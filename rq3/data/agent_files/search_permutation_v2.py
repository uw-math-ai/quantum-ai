import stim
import random
import time
import sys
import copy

def count_cx(circuit):
    cx = 0
    for op in circuit:
        if op.name in ["CX", "CNOT", "CY", "CZ"]:
            cx += len(op.targets_copy()) // 2
    return cx

def count_volume(circuit):
    vol = 0
    for op in circuit:
        if op.name in ["QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "SHIFT_COORDS", "TICK"]:
            continue
        targets = op.targets_copy()
        if op.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP"]:
            vol += len(targets) // 2
        else:
            vol += len(targets)
    return vol

def run():
    print("Loading data...")
    try:
        with open("current_baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        base_cx = count_cx(baseline)
        base_vol = count_volume(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        
        with open("current_stabilizers.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        num_qubits = len(stabilizers[0])
        print(f"Num qubits: {num_qubits}")
        
    except Exception as e:
        print(f"Error loading: {e}")
        return

    best_cx = base_cx
    best_vol = base_vol
    best_circuit_str = None
    
    start_time = time.time()
    iterations = 0
    
    while time.time() - start_time < 60:
        iterations += 1
        
        # Random permutation
        perm = list(range(num_qubits))
        random.shuffle(perm)
        
        # Build permuted stabilizers
        perm_stabs = []
        for s in stabilizers:
            chars = ['I'] * num_qubits
            for old_idx, char in enumerate(s):
                if old_idx < num_qubits:
                    chars[perm[old_idx]] = char
            perm_stabs.append(stim.PauliString("".join(chars)))
            
        try:
            # Synthesis
            tableau = stim.Tableau.from_stabilizers(perm_stabs, allow_underconstrained=True)
            c_perm = tableau.to_circuit("elimination")
            
            # Count CX
            cx = count_cx(c_perm)
            vol = count_volume(c_perm)
            
            # Check improvement
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"Found improvement! Iter {iterations}: CX={cx}, Vol={vol}")
                
                # Reconstruct and Verify
                p_inv = [0]*num_qubits
                for i, p in enumerate(perm):
                    p_inv[p] = i
                
                c_cand = stim.Circuit()
                for op in c_perm:
                    if op.name in ["QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "SHIFT_COORDS", "TICK"]:
                        c_cand.append(op)
                        continue
                    
                    # Remap targets
                    targets = []
                    for t in op.targets_copy():
                        if t.is_qubit_target:
                            targets.append(p_inv[t.value])
                        elif t.is_x_target:
                            targets.append(stim.target_x(p_inv[t.value]))
                        elif t.is_y_target:
                            targets.append(stim.target_y(p_inv[t.value]))
                        elif t.is_z_target:
                            targets.append(stim.target_z(p_inv[t.value]))
                        elif t.is_combiner:
                            targets.append(stim.target_combiner())
                    
                    c_cand.append(op.name, targets, op.gate_args_copy())

                # Verify
                sim = stim.TableauSimulator()
                sim.do(c_cand)
                valid = True
                for s in stabilizers:
                    if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
                        valid = False
                        break
                
                if valid:
                    print("Verification PASSED.")
                    best_cx = cx
                    best_vol = vol
                    best_circuit_str = str(c_cand)
                    
                    with open("best_candidate.stim", "w") as f:
                        f.write(best_circuit_str)
                else:
                    print("Verification FAILED.")
                    
        except Exception as e:
            pass

    print(f"Finished {iterations} iterations.")
    if best_circuit_str:
        print(f"Best found: CX={best_cx}, Vol={best_vol}")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    run()
