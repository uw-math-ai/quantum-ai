import stim
import random
import time

target_stabilizers_str = [
    "IIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX", "IXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXX", "XXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXI", "IIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZ", "IZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ", "ZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZI", "XXIXIIIZZIZIIIZZIZIIIXXIXIIIIIIIIII", "IIIIIIIXXIXIIIZZIZIIIZZIZIIIXXIXIII", "XXIXIIIIIIIIIIXXIXIIIZZIZIIIZZIZIII", "ZZIZIIIXXIXIIIIIIIIIIXXIXIIIZZIZIII"
]

baseline_str = """
CX 30 0 0 30 30 0
H 0 3 13 16 21
CX 0 3 0 13 0 16 0 21 0 25 0 33
H 10 32
CX 10 0 32 0 25 1 1 25 25 1 1 20 1 33
H 5
CX 5 1 10 1 32 1 10 2 2 10 10 2 2 5 2 15 2 33
H 30
CX 30 2 20 3 3 20 20 3 3 33 5 3 15 3 32 3 30 4 4 30 30 4 4 5 5 15 5 33 15 6 6 15 15 6 6 33 33 7 7 33 33 7
H 7 15 24 29 34
CX 7 13 7 15 7 20 7 24 7 26 7 29 7 34
H 11 31
CX 11 7 31 7 15 8 8 15 15 8
H 21
CX 8 21 8 26 11 8 31 8 11 9 9 11 11 9
H 16
CX 9 16 9 21 9 26
H 25
CX 25 9 21 10 10 21 21 10 16 10 31 10 25 11 11 25 25 11 11 26 26 12 12 26 26 12 12 16 16 13 13 16 16 13 32 14 14 32 32 14
S 31 34
H 30 32 33
CX 14 24 14 27 14 29 14 30 14 31 14 32 14 33 14 34
H 26
CX 26 14 26 15 15 26 26 15
H 21
CX 15 21 15 22 33 15 21 16 16 21 21 16 16 17 16 27 33 17 17 33 33 17 17 27 33 18 18 33 33 18 22 18 27 19 19 27 27 19 19 22 22 20 20 22 22 20
H 26 31
CX 21 22 21 26 21 28 21 31 26 22 22 26 26 22 22 23 22 28 22 31 26 23 23 26 26 23 23 28 23 33 31 24 24 31 31 24
S 24
H 24
S 24
CX 24 26
H 30 32
CX 30 24 32 24 34 24 33 25 25 33 33 25 26 25 30 25 32 25 34 25 28 26 26 28 28 26 26 28 28 27 27 28 28 27 30 27 32 27 34 27 32 28 28 32 32 28
H 28 29 30 33
CX 28 29 28 30 28 33 33 29 29 33 33 29
H 31 34
CX 29 31 29 33 29 34 30 32 30 33 30 34
S 34
H 34
CX 33 31 34 31 33 32 34 32
S 34
H 24 25 27
S 24 24 25 25 27 27
H 24 25 27
S 0 0 2 2 4 4 7 7 9 9 11 11 22 22 23 23 27 27
"""

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name == "CX":
            count += len(op.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for op in circuit:
        # Assuming all gates in the circuit are volume gates
        # We approximate volume by total number of operations * targets
        # Or just number of operations.
        # But let's check if the metric is gate count.
        # For graph state, we have H and CZ.
        count += len(op.targets_copy())
        if op.name in ["CX", "CZ", "SWAP"]:
             if len(op.targets_copy()) > 1:
                  # Adjust for 2Q gates if counted differently?
                  # Just stick to len(targets) for now as proxy.
                  pass
    return count

def main():
    baseline = stim.Circuit(baseline_str)
    base_cx = count_cx(baseline)
    print(f"Baseline CX: {base_cx}")

    stabilizers = [stim.PauliString(s) for s in target_stabilizers_str]
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    
    # Try graph state
    try:
        cand_graph = tableau.to_circuit("graph_state")
        cx_graph = count_cx(cand_graph)
        print(f"Graph state CX: {cx_graph}")
        if cx_graph < base_cx:
            print("Graph state is strictly better!")
            with open("candidate.stim", "w") as f:
                f.write(str(cand_graph))
            return
    except Exception as e:
        print(f"Graph state failed: {e}")
        
    # Try permutations with elimination
    print("Trying permutations...")
    best_cx = base_cx
    best_circ = None
    
    # Get number of qubits
    n = len(stabilizers[0])
    qubits = list(range(n))
    
    for i in range(100):
        perm = list(qubits)
        random.shuffle(perm)
        
        # Apply permutation to tableau? No, permute indices before or after?
        # Standard trick: reorder the input stabilizers' qubit indices?
        # Or just use the 'method' of tableau if it supports it.
        # stim doesn't have randomized elimination built-in easily.
        # But we can relabel the tableau.
        
        # P * Tableau * P_inv
        # Synthesize.
        # Apply P_inv * Circuit * P
        
        # To do this cleanly:
        # Create a tableau where we swap columns (qubits).
        # We can't easily swap columns of a tableau in Python without iterating.
        
        # Alternative: Re-parse stabilizers with permuted indices.
        perm_map = {old: new for old, new in zip(qubits, perm)}
        inv_perm_map = {new: old for old, new in zip(qubits, perm)}
        
        # Construct permuted stabilizers
        perm_stabs = []
        for s in stabilizers:
            # s is PauliString.
            # We want to map qubit q -> perm_map[q]
            # Easy way: string manipulation
            s_str = str(s)
            # s_str is "+IX..."
            if s_str.startswith("+"): s_str = s_str[1:]
            
            # This is hard with strings.
            # Use PauliString methods.
            new_s = stim.PauliString(n)
            for k in range(n):
                p = s[k] # 0=I, 1=X, 2=Y, 3=Z
                new_idx = perm_map[k]
                new_s[new_idx] = p
            perm_stabs.append(new_s)
            
        try:
            t_perm = stim.Tableau.from_stabilizers(perm_stabs, allow_underconstrained=True)
            c_perm = t_perm.to_circuit("elimination")
            
            # Now we have a circuit that prepares the permuted state.
            # We need to map the qubits back to match the target.
            # Circuit prepares |psi'> = U |0> where stabilizers are P(S).
            # We want |psi> = P^-1 |psi'> = P^-1 U |0>.
            # So apply P^-1 to the qubits of c_perm.
            
            # Relabel qubits in c_perm: q -> inv_perm_map[q]
            final_circ = stim.Circuit()
            for op in c_perm:
                targets = op.targets_copy()
                new_targets = []
                for t in targets:
                    if t.is_combiner:
                        new_targets.append(t)
                    elif t.is_x_target or t.is_y_target or t.is_z_target: # measurement targets
                         # Handle specialized targets if any (unlikely in elimination)
                         val = t.value
                         new_val = inv_perm_map[val]
                         # create new target
                         # Not easy to construct targets in python simply.
                         # But elimination usually outputs simple gates.
                         pass
                    else:
                        # Simple qubit target
                        val = t.value
                        new_val = inv_perm_map[val]
                        new_targets.append(new_val)
                
                # Reconstruct op is tricky.
                # Easier: just build a map and use circuit.flattened() logic?
                # No, just use circuit string replacement or recreation.
                
                # Let's rely on the fact that elimination only outputs simple gates.
                # CX, H, S, M, R, etc.
                
                # Actually, stim has no 'relabel' method?
                pass
            
            # Let's use string replacement for simplicity if we trust the output format.
            # Or construct a new circuit.
            new_c = stim.Circuit()
            for op in c_perm:
                name = op.name
                args = op.gate_args_copy()
                targets = op.targets_copy()
                new_targets = []
                for t in targets:
                    if t.is_qubit_target:
                         new_targets.append(inv_perm_map[t.value])
                    elif t.is_x_target:
                         new_targets.append(stim.target_x(inv_perm_map[t.value]))
                    elif t.is_y_target:
                         new_targets.append(stim.target_y(inv_perm_map[t.value]))
                    elif t.is_z_target:
                         new_targets.append(stim.target_z(inv_perm_map[t.value]))
                    elif t.is_combiner:
                         new_targets.append(t) # combiners don't have qubit indices
                    else:
                         # Fallback
                         new_targets.append(t)
                
                new_c.append(name, new_targets, args)
            
            cx = count_cx(new_c)
            if cx < best_cx:
                print(f"Found better: {cx}")
                best_cx = cx
                best_circ = new_c
                
        except Exception as e:
            pass # ignore failures

    if best_circ:
        with open("candidate.stim", "w") as f:
            f.write(str(best_circ))
        print("Wrote candidate.stim from permutation.")
    else:
        print("No improvement found via permutations.")

if __name__ == "__main__":
    main()
