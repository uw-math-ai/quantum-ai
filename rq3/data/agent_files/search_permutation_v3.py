import stim
import random
import time
import sys

def count_cx(circuit):
    return circuit.num_2_qubit_gates()

def solve():
    # Load stabilizers
    with open("stabilizers.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Create tableau
    try:
        t_original = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Baseline count (already known to be 839)
    baseline_cx = 839
    print(f"Baseline CX: {baseline_cx}")

    num_qubits = len(t_original)
    qubits = list(range(num_qubits))
    
    best_cx = baseline_cx
    best_perm = None
    best_circuit = None
    
    start_time = time.time()
    attempts = 0
    
    # Try random permutations
    # Also try reverse order
    permutations_to_try = [list(reversed(qubits))]
    
    # Try somewhat local permutations?
    # Just random for now.
    
    while time.time() - start_time < 30: # Run for 30 seconds
        attempts += 1
        if attempts == 1:
            perm = list(range(num_qubits)) # Identity
        elif attempts < len(permutations_to_try) + 2:
            perm = permutations_to_try[attempts-2]
        else:
            perm = list(qubits)
            random.shuffle(perm)
            
        # Create a permutation map: new_index -> old_index
        # We want to reorder the columns of the tableau?
        # Or reorder the qubit labels?
        # If we say physical qubit i is now logical qubit p[i].
        # We want to feed the stabilizers with permuted indices to the synthesis.
        
        # Actually, simpler:
        # 1. Permute the stabilizer strings.
        #    If perm[i] = j, it means the i-th char in string should move to position j?
        #    No, it means qubit i in the original problem is now qubit j.
        #    So if original has X on qubit 0, the new one has X on qubit perm[0].
        
        # 2. Synthesize.
        # 3. Relabel the resulting circuit: qubit j becomes qubit perm^-1[j].
        
        # Let's do this explicitly.
        # Map: old -> new
        forward_map = {i: perm[i] for i in range(num_qubits)}
        # Map: new -> old
        inverse_map = {perm[i]: i for i in range(num_qubits)}
        
        new_stabs = []
        for line in lines:
            # Create a new string or PauliString
            # It's easier to work with PauliString objects
            ps = stim.PauliString(line)
            new_ps = stim.PauliString(num_qubits)
            for k in range(len(ps)):
                op = ps[k]
                if op: # 1=X, 2=Y, 3=Z
                    new_idx = forward_map.get(k, k) # Handle if num_qubits mismatch?
                    if new_idx < num_qubits:
                         new_ps[new_idx] = op
            new_stabs.append(new_ps)
            
        # Synthesize
        try:
            t = stim.Tableau.from_stabilizers(new_stabs, allow_underconstrained=True)
            c = t.to_circuit(method="elimination")
            cx = count_cx(c)
            
            if cx < best_cx:
                print(f"Found better! CX: {cx} (Attempt {attempts})")
                best_cx = cx
                best_perm = list(perm)
                # Relabel back
                # Circuit has gates on 'new' indices. We map them back to 'old'.
                # qubit q in circuit -> inverse_map[q]
                
                # Unfortunately stim circuit relabeling isn't built-in easily for arbitrary maps?
                # Can we just create a map array?
                # c_relabelled = c.with_qubits_mapped(inverse_map) # Hypothetical
                
                # Manual relabeling
                c_str = str(c)
                # This is risky and slow to parse text.
                # But we only do it for the best one.
                
                # Better: keep the 'best_circuit' as the permuted one, and only relabel at the end.
                best_circuit = c
                
        except Exception as e:
            pass
            
    if best_circuit:
        print(f"Best found CX: {best_cx}")
        # Relabel and save
        # Map new_idx -> old_idx
        # inverse_map[new_idx] = old_idx
        
        # We need to construct a relabeling array for stim
        # invalid indices map to... themselves?
        # Stim expects a list where index i is the new target for qubit i.
        # Wait, usually `with_qubits_mapped` takes a dict or list?
        # Stim doesn't have `with_qubits_mapped` in Python API directly on Circuit?
        # Let's check documentation or assume no.
        # I'll iterate the instructions.
        
        final_c = stim.Circuit()
        for instr in best_circuit:
            targets = []
            for t in instr.targets_copy():
                if t.is_qubit_target:
                    targets.append(inverse_map[t.value])
                else:
                    targets.append(t) # Measurement targets etc?
            final_c.append(instr.name, targets, instr.gate_args)
            
        print(f"Final circuit CX: {count_cx(final_c)}")
        final_c.to_file("candidate_perm.stim")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    solve()
