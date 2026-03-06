import stim
import sys
import random

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        name = instr.name
        
        # CX count
        if name in ["CX", "CNOT"]:
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG", "C_XYZ", "C_ZYX"]:
             n_targets = len(instr.targets_copy())
             if name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG", "C_XYZ", "C_ZYX"]:
                 vol += n_targets // 2
             else:
                 vol += n_targets
        elif name in ["R", "RX", "RY", "RZ", "M", "MX", "MY", "MZ", "MPP", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK", "SHIFT_COORDS", "QUBIT_COORDS"]:
            pass
            
    return cx, vol

def permute_stabilizers(stabs, p):
    # p[old] = new
    new_stabs = []
    n_qubits = len(p)
    for s in stabs:
        new_pauli = stim.PauliString(n_qubits)
        for i in range(len(s)):
            val = s[i] # 0=I, 1=X, 2=Y, 3=Z
            if val:
                # Map index i to p[i]
                if i < n_qubits:
                    new_target = p[i]
                    if val == 1: new_pauli[new_target] = "X"
                    elif val == 2: new_pauli[new_target] = "Y"
                    elif val == 3: new_pauli[new_target] = "Z"
        new_stabs.append(new_pauli * s.sign)
    return new_stabs

def remap_circuit(circ, p_inv):
    # p_inv[new] = old
    new_circ = stim.Circuit()
    for instr in circ:
        targets = instr.targets_copy()
        new_targets = []
        for t in targets:
            if t.is_qubit_target:
                new_targets.append(p_inv[t.value])
            else:
                new_targets.append(t) # Measurement targets etc might need handling if used
        new_circ.append(instr.name, new_targets, instr.gate_args_copy())
    return new_circ

def solve():
    print("Loading baseline...")
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\current_baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    b_cx, b_vol = count_metrics(baseline)
    print(f"Baseline: CX={b_cx}, Vol={b_vol}")

    print("Loading stabilizers...")
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\current_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        stabs = [stim.PauliString(l) for l in lines]
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    n_qubits = len(stabs[0])
    print(f"Qubits: {n_qubits}")
    
    # Check max qubit index in baseline
    max_q = 0
    for instr in baseline:
        for t in instr.targets_copy():
             if t.is_qubit_target:
                 max_q = max(max_q, t.value)
    
    print(f"Max qubit in baseline: {max_q}")
    n_qubits = max(n_qubits, max_q + 1)
    
    indices = list(range(n_qubits))
    
    best_cx = b_cx
    best_vol = b_vol
    best_circ = None
    
    # Try normal synthesis first (Identity permutation)
    # Already done in previous step, but let's include it
    
    import time
    start_time = time.time()
    
    for i in range(1000):
        if i == 0:
            p = indices[:] # Identity
        else:
            random.shuffle(indices)
            p = indices[:]
            
        # p maps old -> new
        
        # Permute stabilizers
        p_stabs = permute_stabilizers(stabs, p)
        
        try:
            # allow_underconstrained=True
            tableau = stim.Tableau.from_stabilizers(p_stabs, allow_underconstrained=True, allow_redundant=True)
            c_p = tableau.to_circuit(method="elimination")
            
            # Map back
            p_inv = [0]*n_qubits
            for old_idx, new_idx in enumerate(p):
                p_inv[new_idx] = old_idx
                
            c_cand = remap_circuit(c_p, p_inv)
            
            cx, vol = count_metrics(c_cand)
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"Iter {i}: FOUND IMPROVEMENT! CX={cx}, Vol={vol}")
                best_cx = cx
                best_vol = vol
                best_circ = c_cand
                
                # Verify immediately to be sure
                sim = stim.TableauSimulator()
                sim.do(c_cand)
                valid = True
                for s in stabs:
                    if sim.peek_observable_expectation(s) != 1:
                        valid = False
                        break
                if valid:
                    print("  VALID.")
                    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate.stim", "w") as f:
                        f.write(str(c_cand))
                else:
                    print("  INVALID (Should not happen).")
            
        except Exception as e:
            # print(f"Error in iter {i}: {e}")
            pass
            
        if time.time() - start_time > 100: # 100 seconds limit
            print("Time limit reached.")
            break
            
    print(f"Final Best: CX={best_cx}, Vol={best_vol}")

if __name__ == "__main__":
    solve()
