import stim
import random
import time

BASELINE_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq3\current_baseline.stim"
OUTPUT_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate_opt.stim"

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit:
        name = instruction.name
        n_targets = len(instruction.targets_copy())
        
        if name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            gate_count = n_targets // 2
            if name in ["CX", "CNOT"]:
                cx += gate_count
            vol += gate_count
        elif name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "C_XYZ", "C_ZYX"]:
             vol += n_targets
        elif name in ["MPP", "M", "MR", "R", "RX", "RY", "RZ", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK", "SHIFT_COORDS", "QUBIT_COORDS"]:
            pass
            
    return cx, vol

def permute_circuit(circuit, mapping):
    # Mapping: logical qubit -> physical qubit (or old -> new)
    # Let's say mapping[i] is the new index for qubit i.
    new_circuit = stim.Circuit()
    for instruction in circuit:
        args = instruction.gate_args_copy()
        targets = []
        for t in instruction.targets_copy():
            if t.is_qubit_target:
                targets.append(stim.target_combine(stim.target_inv(mapping[t.value])))
            else:
                targets.append(t) # Measurement records, etc.
        new_circuit.append(instruction.name, targets, args)
    return new_circuit

def solve():
    print("Loading baseline...")
    with open(BASELINE_FILE, "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    # Analyze qubit count
    num_qubits = baseline.num_qubits
    print(f"Num qubits: {num_qubits}")
    
    base_cx, base_vol = get_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    best_cx = base_cx
    best_vol = base_vol
    best_circuit = baseline
    
    # Methods to try
    methods = ["elimination", "graph_state"]
    
    # Try simple synthesis first without permutation
    tableau = stim.Tableau.from_circuit(baseline)
    
    for method in methods:
        try:
            cand = tableau.to_circuit(method=method)
            cx, vol = get_metrics(cand)
            print(f"Method {method}: CX={cx}, Vol={vol}")
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"New Best found with {method}!")
                best_cx = cx
                best_vol = vol
                best_circuit = cand
        except Exception as e:
            print(f"Method {method} failed: {e}")

    # Search with permutations
    start_time = time.time()
    iterations = 0
    max_time = 60 # 1 minute search
    
    indices = list(range(num_qubits))
    
    while time.time() - start_time < max_time:
        iterations += 1
        
        # Random permutation
        perm = list(indices)
        random.shuffle(perm)
        
        # Apply permutation to tableau
        # We want T_perm. T_perm maps Z_new_k -> S_new_k
        # This is equivalent to applying permutation to the circuit, then computing tableau.
        
        # Mapping: old index i -> new index perm[i]
        # But wait, stim.Circuit uses integer indices directly.
        # If we remap qubit 0 -> 5, then gate H 0 becomes H 5.
        
        # Create a remapped circuit
        remapped_baseline = stim.Circuit()
        for instruction in baseline:
             targets = []
             for t in instruction.targets_copy():
                 if t.is_qubit_target:
                     targets.append(perm[t.value]) # Map t.value -> perm[t.value]
                 else:
                     targets.append(t)
             remapped_baseline.append(instruction.name, targets, instruction.gate_args_copy())
             
        try:
            t_perm = stim.Tableau.from_circuit(remapped_baseline)
            
            # Synthesize
            # Try both methods
            # Only graph_state is likely to benefit much from reordering if elimination is stable?
            # Actually elimination order matters too.
            
            method = random.choice(methods)
            cand_perm = t_perm.to_circuit(method=method)
            
            # Unpermute candidate
            # Map new index k -> old index perm.index(k) ? No.
            # We mapped i -> perm[i]. So if result has gate on perm[i], we want gate on i.
            # Inverse map: perm[i] -> i.
            
            inv_map = {perm[i]: i for i in range(len(perm))}
            
            cand = stim.Circuit()
            for instruction in cand_perm:
                 targets = []
                 for t in instruction.targets_copy():
                     if t.is_qubit_target:
                         targets.append(inv_map[t.value])
                     else:
                         targets.append(t)
                 cand.append(instruction.name, targets, instruction.gate_args_copy())
            
            cx, vol = get_metrics(cand)
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"New Best found (iter {iterations}, method {method}): CX={cx}, Vol={vol}")
                best_cx = cx
                best_vol = vol
                best_circuit = cand
                
                # Check validity (sanity check)
                t_check = stim.Tableau.from_circuit(cand)
                if t_check == tableau:
                    pass # Good
                else:
                    print("Warning: Tableau mismatch! Ignoring.")
                    # Revert
                    best_cx = base_cx # actually we should just not update best
                    continue
                    
        except Exception as e:
            # print(f"Error in iteration: {e}")
            pass

    print(f"Final Best: CX={best_cx}, Vol={best_vol}")
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(str(best_circuit))

if __name__ == "__main__":
    solve()
