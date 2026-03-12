import stim
import random
import sys

def count_volume(circuit):
    # Simple count: CZ is 1, single qubit is 1.
    # CX, CY, CZ, H, S, SQRT_X etc are volume 1.
    count = 0
    for instr in circuit:
        if instr.name in ["TICK", "QUBIT_COORDS", "SHIFT_COORDS"]:
            continue
        # For gates with multiple targets, stim usually unrolls them or counts them as 1?
        # The metric likely counts operations.
        # But 'CX 0 1 2 3' is 2 CX gates.
        # So we iterate over args.
        # But for graph state, we usually have distinct gates.
        # Let's count instructions * number of pairwise/single ops?
        # Instruction 'H 0 1' is 2 H gates.
        if instr.name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "CV", "CY", "ZC", "XC", "Y", "C_XYZ", "C_ZYX"]:
             # 2-qubit gates
             # Length of targets / 2
             count += len(instr.targets) // 2
        else:
             # 1-qubit gates
             count += len(instr.targets)
    return count

def solve():
    with open("target_stabilizers_rq3_unique_123.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    num_qubits = 49 # From prompt
    
    # Original stabilizers
    original_paulis = [stim.PauliString(line) for line in lines]
    
    best_volume = 999999
    best_circuit = None
    best_perm = None

    # Try 50 permutations
    for i in range(50):
        # Generate random permutation
        perm = list(range(num_qubits))
        random.shuffle(perm)
        
        # Create map: old -> new
        # old index j maps to perm[j]
        # But stim doesn't have a direct 'remap_pauli' for list of ints?
        # We can construct new PauliStrings manually.
        
        # More efficiently:
        # Create a Tableau from original stabilizers.
        # Then apply permutation? No, Tableau doesn't support easy permutation of qubits.
        
        # Let's just remap the PauliStrings.
        # PS[k] on qubit j becomes PS[k] on qubit perm[j].
        
        # But wait, stim.PauliString doesn't have random access assignment easily.
        # Easier: convert to string, shuffle characters?
        # original string: "IXYZ..." corresponding to 0, 1, 2, 3...
        # new string at index k comes from original string at index perm_inv[k]?
        # Let's think:
        # We want to process qubit `perm[j]` as if it was qubit `j`.
        # No, we want to assign the role of "pivot 0" to qubit `perm[0]`.
        # So we want to feed the synthesis algorithm a permuted set of stabilizers.
        
        # Let q_new = perm[q_old].
        # Stabilizer S acts on q_old with P.
        # New stabilizer S' acts on q_new with P.
        
        # So S'[perm[j]] = S[j].
        # So S'[k] = S[perm_inv[k]].
        
        # Let's build the permuted strings.
        perm_inv = [0] * num_qubits
        for j, p in enumerate(perm):
            perm_inv[p] = j
            
        # Actually, simpler:
        # Create a circuit that permutes 0->perm[0], etc? No.
        
        # Let's just use stim's remapping on the OUTPUT circuit.
        # If we feed the ORIGINAL stabilizers to graph_state, we get a circuit C.
        # Graph state algorithm picks pivots 0, 1, 2...
        # If we want it to pick pivots perm[0], perm[1]...
        # We should rename qubits in the input stabilizers:
        # Qubit j becomes Qubit perm[j].
        # So if orig stab has X on 0, new stab has X on perm[0].
        
        new_paulis = []
        for p in original_paulis:
            new_p = stim.PauliString(num_qubits)
            for k in range(num_qubits):
                # new_p at index perm[k] gets p at index k
                # (This is correct: we are moving the Pauli term from k to perm[k])
                # stim.PauliString.__getitem__ returns 0,1,2,3 for I,X,Y,Z
                val = p.get(k) # .get returns integer 0-3
                if val:
                    new_p[perm[k]] = val # using __setitem__ or similar?
                    # valid syntax for stim > 1.12: ps[k] = "X" or int
            new_paulis.append(new_p)
            
        # Synthesize
        try:
            t = stim.Tableau.from_stabilizers(new_paulis, allow_redundant=True, allow_underconstrained=True)
            c = t.to_circuit(method="graph_state")
            
            # Count volume of c
            # Note: c acts on qubits perm[j].
            # We don't need to remap back to count volume (metrics are invariant under relabeling).
            vol = count_volume(c)
            
            if vol < best_volume:
                best_volume = vol
                # Remap back to store the valid candidate
                # We need a circuit that acts on original qubits.
                # Current circuit acts on 'new' qubits (perm[j]).
                # We want to map perm[j] -> j.
                # So map k -> perm_inv[k].
                
                # Check stim.Circuit.with_qubits_remapped
                # It takes a dictionary or map.
                # map[old_index] = new_index
                # Here 'old_index' is the index in 'c' (which is perm[j]).
                # 'new_index' is j.
                # So we want map[perm[j]] = j.
                # This is exactly perm_inv.
                
                remap_dict = {p: i for i, p in enumerate(perm)}
                # Or just list where list[k] is the new target for k.
                # list[k] = perm_inv[k].
                
                c_orig = c.with_qubits_remapped(remap_dict)
                best_circuit = c_orig
                best_perm = perm
                print(f"New best volume: {vol}")
                
        except Exception as e:
            continue

    # Post process best circuit (RX -> H)
    if best_circuit:
        final_circuit = stim.Circuit()
        for instr in best_circuit:
            if instr.name == "RX":
                final_circuit.append("H", instr.targets_copy())
            elif instr.name == "R" or instr.name == "RZ":
                 pass
            elif instr.name == "M":
                 final_circuit.append(instr)
            else:
                final_circuit.append(instr)
                
        with open("candidate_rq3_optimized.stim", "w") as f:
            f.write(str(final_circuit))

if __name__ == "__main__":
    solve()
