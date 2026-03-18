import stim
import random
import sys
import time

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
            if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instruction.targets_copy()) // 2
            else:
                count += len(instruction.targets_copy())
    return count

def solve():
    # Load target stabilizers
    with open("target_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    stabs = [stim.PauliString(l) for l in lines]
    
    num_qubits = len(stabs[0])
    print(f"Loaded {len(stabs)} stabilizers on {num_qubits} qubits.")

    # Baseline metrics
    base_cx = 911
    base_vol = 966
    print(f"Target to beat: CX < {base_cx} OR (CX == {base_cx} AND Vol < {base_vol})")

    best_circuit = None
    best_cx = float('inf')
    best_vol = float('inf')

    methods = ["elimination", "graph_state"]
    
    start_time = time.time()
    num_iter = 200
    
    # Also try identity permutation first
    permutations_to_try = [list(range(num_qubits))] 
    
    for _ in range(num_iter):
        p = list(range(num_qubits))
        random.shuffle(p)
        permutations_to_try.append(p)

    print(f"Starting search with {len(permutations_to_try)} permutations...")

    for i, perm in enumerate(permutations_to_try):
        if time.time() - start_time > 600: # 10 minute timeout
            break
            
        inv_perm = [0] * num_qubits
        for idx, p in enumerate(perm):
            inv_perm[p] = idx

        # Permute stabilizers
        perm_stabs = []
        for s in stabs:
            new_s = stim.PauliString(num_qubits)
            for k in range(num_qubits):
                p_val = s[k]
                if p_val != 0:
                    new_s[perm[k]] = p_val
            perm_stabs.append(new_s)

        try:
            tableau = stim.Tableau.from_stabilizers(perm_stabs, allow_underconstrained=True, allow_redundant=True)
            
            for method in methods:
                try:
                    syn_circ = tableau.to_circuit(method)
                    
                    # Map back
                    cand = stim.Circuit()
                    for instr in syn_circ:
                        targets = instr.targets_copy()
                        new_targets = []
                        for t in targets:
                            if t.is_qubit_target:
                                new_targets.append(inv_perm[t.value])
                            else:
                                new_targets.append(t)
                        cand.append(instr.name, new_targets, instr.gate_args_copy())

                    cx = count_cx(cand)
                    vol = count_volume(cand)

                    # Check improvement
                    is_better = False
                    if cx < base_cx:
                        is_better = True
                    elif cx == base_cx and vol < base_vol:
                        is_better = True
                    
                    if is_better:
                        # Check validity only if better (optimization)
                        sim = stim.TableauSimulator()
                        sim.do(cand)
                        valid = True
                        for s in stabs:
                            if sim.peek_observable_expectation(s) != 1:
                                valid = False
                                break
                        
                        if valid:
                            if cx < best_cx or (cx == best_cx and vol < best_vol):
                                print(f"Iter {i} ({method}): NEW BEST! CX={cx}, Vol={vol}")
                                best_cx = cx
                                best_vol = vol
                                best_circuit = cand
                                with open("best_candidate.stim", "w") as f:
                                    f.write(str(cand))
                        else:
                             pass # Invalid
                    
                    # Also keep track if it's the first valid one we see, even if not strictly better (fallback)
                    # But prompt requires strict improvement.
                except Exception as e:
                    pass
        except Exception as e:
            pass

    print(f"Search finished. Best: CX={best_cx}, Vol={best_vol}")

if __name__ == "__main__":
    solve()
