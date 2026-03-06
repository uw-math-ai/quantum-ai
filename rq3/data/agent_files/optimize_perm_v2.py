import stim
import random
import sys
import numpy as np

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            count += len(instr.targets_copy()) // 2
    return count

def compute_volume(circuit):
    count = 0
    for instr in circuit:
        # Volume is total gate count.
        # Decomposition: 
        # H 0 1 2 -> H 0, H 1, H 2 (3 gates)
        # CX 0 1 2 3 -> CX 0 1, CX 2 3 (2 gates)
        
        n_args = len(instr.targets_copy())
        if instr.name in ["CX", "CY", "CZ", "CNOT", "SWAP", "ISWAP"]:
            count += n_args // 2
        elif instr.name in ["H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
            count += n_args
        # Ignore measurements for volume if not gate-based?
        # Usually volume includes all operations.
    return count

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    return [stim.PauliString(l) for l in lines]

def permute_stabilizers(stabilizers, perm):
    # perm[old_index] = new_index
    # We want to create new stabilizers such that:
    # S_new[new_index] = S_old[old_index]
    # S_new[j] = S_old[perm_inv[j]]
    
    num_qubits = len(stabilizers[0])
    
    # Create inverse permutation
    inv_perm = [0] * num_qubits
    for i, p in enumerate(perm):
        inv_perm[p] = i
        
    new_stabs = []
    for s in stabilizers:
        # s is old stabilizer
        # We construct new stabilizer
        
        # Get dense Pauli indices (0=I, 1=X, 2=Y, 3=Z)
        # Or just use string rep if easier, but stim objects are better
        
        # Let's use numpy access
        # s has (xs, zs) bits
        # new_s will have (new_xs, new_zs)
        
        # new_xs[j] = xs[inv_perm[j]]
        
        # But wait, stabilizers might be shorter than num_qubits if loaded from string without padding?
        # The file has explicit "IIII..." so length should match.
        
        new_s = stim.PauliString(num_qubits)
        
        # Iterate over all indices
        # This is slow in python loop but fine for 54 qubits
        for new_idx in range(num_qubits):
            old_idx = inv_perm[new_idx]
            p = s[old_idx] # returns 0,1,2,3
            new_s[new_idx] = p
            
        new_stabs.append(new_s)
        
    return new_stabs

def inverse_permute_circuit(circuit, perm):
    # circuit acts on new_indices.
    # We want circuit acting on old_indices.
    # The circuit instruction on qubit `q_new` corresponds to operation on `q_old` such that `perm[q_old] == q_new`.
    # So `q_old` = `inv_perm[q_new]`.
    
    inv_perm = [0] * len(perm)
    for i, p in enumerate(perm):
        inv_perm[p] = i
        
    new_circuit = stim.Circuit()
    for instr in circuit:
        new_targets = []
        for t in instr.targets_copy():
            if t.is_qubit_target:
                new_targets.append(inv_perm[t.value])
            elif t.is_x_target:
                 new_targets.append(stim.target_x(inv_perm[t.value]))
            elif t.is_y_target:
                 new_targets.append(stim.target_y(inv_perm[t.value]))
            elif t.is_z_target:
                 new_targets.append(stim.target_z(inv_perm[t.value]))
            else:
                new_targets.append(t)
        
        new_circuit.append(instr.name, new_targets, instr.gate_args_copy())
        
    return new_circuit

def main():
    try:
        stabilizers = load_stabilizers("stabilizers_54.txt")
        num_qubits = len(stabilizers[0])
        print(f"Num qubits: {num_qubits}")
        
        baseline_cx = 237
        baseline_vol = 250
        
        print(f"Baseline: CX={baseline_cx}, Vol={baseline_vol}")
        
        best_cx = baseline_cx
        best_vol = baseline_vol
        
        # Try random permutations
        for i in range(100):
            perm = list(range(num_qubits))
            random.shuffle(perm)
            
            # 1. Permute stabilizers
            stabs_perm = permute_stabilizers(stabilizers, perm)
            
            # 2. Synthesize
            try:
                tableau = stim.Tableau.from_stabilizers(stabs_perm, allow_redundant=True, allow_underconstrained=True)
                synth_circuit = tableau.to_circuit("elimination")
                
                # 3. Check metrics on synthesized circuit (acting on permuted qubits)
                # Wait, metrics are invariant under permutation for CX count and Volume (since gate types don't change).
                # So we can check metrics directly on synth_circuit!
                # If good, THEN inverse permute and save.
                
                cx = count_cx(synth_circuit)
                vol = compute_volume(synth_circuit)
                
                if cx < best_cx or (cx == best_cx and vol < best_vol):
                    print(f"Found IMPROVEMENT at iter {i}: CX={cx}, Vol={vol}")
                    best_cx = cx
                    best_vol = vol
                    
                    final_circuit = inverse_permute_circuit(synth_circuit, perm)
                    
                    with open("candidate_perm.stim", "w") as f:
                         f.write(str(final_circuit))
                         
            except Exception as e:
                # print(f"Failed iter {i}: {e}")
                pass

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
