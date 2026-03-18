import stim
import random
import copy

def count_cz(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CZ":
            # CZ targets pairs, so number of gates is len(targets)/2
            count += len(instr.targets_copy()) // 2
    return count

def main():
    stabilizers = []
    with open('target_stabilizers_current.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))

    # Determine num qubits from the first stabilizer
    num_qubits = len(stabilizers[0])
    qubit_indices = list(range(num_qubits))

    best_cz_count = float('inf')
    best_circuit = None
    
    # Try original order first
    orders_to_try = [qubit_indices]
    # Add random permutations
    for _ in range(2000):
        perm = list(qubit_indices)
        random.shuffle(perm)
        orders_to_try.append(perm)

    print(f"Searching {len(orders_to_try)} permutations...")

    for i, p_map in enumerate(orders_to_try):
        # p_map[k] = original_index_at_position_k
        # We want to map original stabilizers to new labels.
        # Stabilizer S on qubit q should move to position where q is?
        # No, let's think about it as relabeling.
        # If we just reorder the columns of the stabilizer matrix.
        # We want to construct a new list of PauliStrings where the k-th Pauli 
        # is the p_map[k]-th Pauli of the original string.
        # Wait. 
        # If I permute qubits, I am saying "Physical Qubit 0 is now Logical Qubit p[0]".
        # No, simpler:
        # Let's say I have a function `permute_pauli_string(ps, permutation)`
        # that returns a new PauliString where the gate at index i comes from index permutation[i] of original.
        # No, that's creating a new state.
        
        # Correct approach:
        # 1. Map stabilizer S to S_permuted using P.
        #    S_permuted acts on qubit i as S acted on P[i].
        #    Wait. If I swap q0 and q1. 
        #    S = X0 Z1.
        #    P = [1, 0]. (q0->1, q1->0).
        #    S_permuted should be X1 Z0.
        #    So S_permuted[i] = S[P[i]]. (Gate at new index i comes from old index P[i]).
        #    Let's verify.
        #    New qubit 0 is old qubit 1. So gate on new 0 should be gate on old 1 (Z).
        #    New qubit 1 is old qubit 0. So gate on new 1 should be gate on old 0 (X).
        #    So new string is Z0 X1.
        #    Yes. S_perm[i] = S[P[i]].
        
        # 2. Synthesize circuit C_perm for S_perm.
        #    C_perm acts on indices 0..N-1.
        
        # 3. Map C_perm back to C_original.
        #    Gate on qubit i in C_perm should act on P[i] in C_original.
        #    Wait.
        #    In step 1, we said "New qubit i corresponds to Old qubit P[i]".
        #    So if C_perm has "H 0", it means "H on New Qubit 0".
        #    Which is "H on Old Qubit P[0]".
        #    So yes, replace target i with P[i].
        
        # Let's implement this.
        
        current_stabilizers = []
        for s in stabilizers:
            new_gates = [0] * num_qubits
            # s[k] returns 0,1,2,3 for I,X,Y,Z
            # We want new_gates[i] = s[p_map[i]]
            # But stim.PauliString is not easily indexable like that in all versions?
            # It is iterable.
            # Use a string representation or similar.
            # s_str = str(s) # e.g. "+XZ..."
            # Careful with sign.
            # Assuming +1 sign for all target stabilizers as per file format (no sign char usually).
            # The file has IIXI... so it's just Paulis.
            
            # Efficient way:
            new_s = stim.PauliString(num_qubits)
            # This is slow if we do it for every string.
            # Better: construct the list of Paulis then create string.
            
            # Let's assume s is indexable or convertible.
            # s_val = s.to_numpy() ? No.
            # Let's just use string manipulation.
            s_str = str(s)
            sign = ""
            if s_str.startswith('+') or s_str.startswith('-'):
                sign = s_str[0]
                s_str = s_str[1:]
            else:
                s_str = s_str[1:] # Stim PauliStrings print with + by default often.
                # Wait, check the file format. The file has "IIXI..."
                # stim.PauliString("IIXI") -> str might be "+IIXI"
            
            # Actually, `target_stabilizers_current.txt` has just "IIXI..." lines.
            # So s is created from that.
            
            # Let's just rely on the fact that we can create a PauliString from a list of gate indices.
            # gates = [s.get(k) for k in range(num_qubits)] # if get exists
            # Or iterate.
            
            # Workaround:
            # Create a string for the new PauliString.
            # P[i] is the OLD index that maps to NEW index i.
            # gate at i = gate at P[i]
            
            # Need to get gates from s.
            # `len(s)` is num_qubits.
            # We can use `s[k]`? In recent Stim versions yes.
            # If not, `str(s)` gives "+IXYZ...".
            
            s_str_full = str(s)
            s_content = s_str_full[1:] if s_str_full[0] in '+-' else s_str_full
            # Construct new string
            new_chars = [''] * num_qubits
            for new_idx in range(num_qubits):
                old_idx = p_map[new_idx]
                new_chars[new_idx] = s_content[old_idx]
            
            new_s_str = s_str_full[0] + "".join(new_chars) if s_str_full[0] in '+-' else "".join(new_chars)
            current_stabilizers.append(stim.PauliString(new_s_str))
            
        try:
            tableau = stim.Tableau.from_stabilizers(current_stabilizers, allow_redundant=True, allow_underconstrained=True)
            circuit = tableau.to_circuit(method="graph_state")
            
            # Count CZ
            cz_count = count_cz(circuit)
            
            # Also check volume (total gates)?
            # Lexicographic: cx_count (0 always here), then volume.
            # So just minimize volume.
            # Volume = number of operations in circuit.
            # But graph state always has H layer + CZ layer + local layer.
            # CZ count is the main variable.
            # Local Cliffords count too.
            # Let's use circuit.num_operations? No, CZ 0 1 2 3 counts as 1 op but 2 gates?
            # Stim's `len(circuit)` counts instructions.
            # A merged CZ instruction CZ 0 1 2 3 counts as 1 instruction.
            # But the metric `volume` counts actual gates.
            # `evaluate_optimization` computes volume.
            # Rough proxy: len(circuit) or sum of arguments.
            # Let's just minimize CZ count (number of edges).
            
            if cz_count < best_cz_count:
                best_cz_count = cz_count
                
                # Map back
                mapped_circuit = stim.Circuit()
                for instr in circuit:
                    targets = instr.targets_copy()
                    new_targets = []
                    for t in targets:
                         if t.is_qubit_target:
                             # t.value is the qubit index in the PERMUTED circuit (new index)
                             # We want the OLD index.
                             # P[new_index] = old_index
                             new_targets.append(t.value + (p_map[t.value] - t.value)) # simplified: p_map[t.value]
                         else:
                             new_targets.append(t)
                             
                    # Reconstruct instruction
                    # Note: constructing instruction with integer targets assumes qubit targets.
                    # Stim 1.12+: valid.
                    mapped_circuit.append(instr.name, [p_map[t.value] if t.is_qubit_target else t for t in targets])

                # Replace RX with H
                final_circuit = stim.Circuit()
                for instr in mapped_circuit:
                    if instr.name == "RX":
                        final_circuit.append("H", instr.targets_copy())
                    else:
                        final_circuit.append(instr)
                
                best_circuit = final_circuit
                print(f"New best CZ count: {cz_count}")

        except Exception as e:
            continue

    if best_circuit:
        with open('candidate_opt.stim', 'w') as f:
            print(best_circuit, file=f)
        print("Written best candidate to candidate_opt.stim")
    else:
        print("No valid candidate found.")

if __name__ == "__main__":
    main()
