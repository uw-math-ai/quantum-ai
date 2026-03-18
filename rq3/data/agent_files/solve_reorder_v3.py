import stim
import random

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT"]:
            n = len(instruction.targets_copy()) // 2
            cx += n
            vol += n
        elif instruction.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
             n = len(instruction.targets_copy()) // 2
             vol += n
        else:
             vol += len(instruction.targets_copy())
    return cx, vol

def permute_pauli(p, pi):
    # p is stim.PauliString
    # pi is list where pi[old_index] = new_index
    n = len(pi)
    new_p = stim.PauliString(n)
    
    # Iterate over active Paulis
    # p is iterable yielding (index, type_int) ? No.
    # p[i] gives int.
    for i in range(len(p)):
        val = p[i]
        if val: # 1=X, 2=Y, 3=Z
            if i < len(pi):
                target = pi[i]
                if val == 1: new_p[target] = "X"
                elif val == 2: new_p[target] = "Y"
                elif val == 3: new_p[target] = "Z"
    return new_p * p.sign

def relabel_circuit(circ, mapping):
    # mapping[old] = new
    # But here we want to map synthesized qubit k (which corresponds to pi[k]?) back to k?
    # No.
    # Synthesized circuit C' acts on new indices.
    # Gate on target t in C' applies to qubit t.
    # We want to map t back to pi^-1(t).
    # So mapping should be pi_inv.
    new_circ = stim.Circuit()
    for instruction in circ:
        new_targets = []
        for t in instruction.targets_copy():
            if t.is_qubit_target:
                new_targets.append(mapping[t.value])
            else:
                new_targets.append(t)
        new_circ.append(instruction.name, new_targets, instruction.gate_args_copy())
    return new_circ

def solve():
    print("Loading baseline...")
    try:
        baseline = stim.Circuit.from_file("my_baseline.stim")
    except Exception as e:
        print(e)
        return

    base_cx, base_vol = count_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")

    # Get tableau
    t_base = stim.Tableau.from_circuit(baseline)
    n = len(t_base)
    print(f"Qubits: {n}")
    
    best_circ = None
    best_metrics = (base_cx, base_vol)

    indices = list(range(n))
    
    # Try 200 random permutations
    for i in range(200):
        random.shuffle(indices)
        pi = indices
        
        # Construct inverse mapping
        pi_inv = [0] * n
        for old, new in enumerate(pi):
            pi_inv[new] = old
            
        # Build T_new
        xs = []
        zs = []
        for k in range(n):
            # Qubit k in new ordering corresponds to pi_inv[k] in old
            # We want to know what X_k maps to in the new tableau.
            # In the old tableau, X_{pi_inv[k]} maps to P.
            # In the new tableau, X_k corresponds to X_{pi_inv[k]} logic.
            # So it should map to Permute(P).
            
            old_k = pi_inv[k]
            
            old_x = t_base.x_output(old_k)
            old_z = t_base.z_output(old_k)
            
            new_x = permute_pauli(old_x, pi)
            new_z = permute_pauli(old_z, pi)
            
            xs.append(new_x)
            zs.append(new_z)
            
        try:
            # Create tableau using from_conjugated_generators?
            # No, that's not exactly right.
            # We want tableau T' such that T'(X_k) = xs[k], T'(Z_k) = zs[k].
            # This is exactly what stim.Tableau.from_conjugated_generators does
            # if we pass the generators for X_k and Z_k.
            # Actually, from_conjugated_generators(xs, zs) creates a tableau T such that T(X_k) = xs[k], T(Z_k) = zs[k].
            # Yes.
            
            t_new = stim.Tableau.from_conjugated_generators(
                xs=xs,
                zs=zs
            )
            
            c_new = t_new.to_circuit("elimination")
            
            # Now relabel c_new back
            # Gate on k -> Gate on pi_inv[k]
            c_final = relabel_circuit(c_new, pi_inv)
            
            cx, vol = count_metrics(c_final)
            
            if cx < best_metrics[0] or (cx == best_metrics[0] and vol < best_metrics[1]):
                print(f"  Iteration {i}: IMPROVEMENT! CX={cx}, Vol={vol}")
                best_metrics = (cx, vol)
                best_circ = c_final
                with open("candidate.stim", "w") as f:
                    f.write(str(c_final))
        except Exception as e:
            # print(f"Error: {e}")
            pass

    if best_circ:
        print("Found improvement.")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    solve()
