import stim
import sys

def find_bad_faults():
    circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim")
    data_qubits = range(circuit.num_qubits)
    threshold = (9 - 1) // 2  # 4
    
    bad_faults = []
    
    # We need to iterate through operations.
    # To efficiently propagate, we can compute the tableau of the suffix.
    # But suffix changes every gate.
    # We can iterate backwards.
    # Start with identity tableau (end of circuit).
    # Inverse of gate G is G^{-1}.
    # Conjugating by G^{-1} moves error from "after G" to "after G^{-1} applied to end state" ... wait.
    # Let's say we have circuit G1 G2 ... GN.
    # Error E after G_i.
    # Propagates through G_{i+1} ... GN.
    # Final error E' = (G_{i+1}...GN) E (G_{i+1}...GN)^\dagger.
    # Let T_k be the tableau of G_k ... GN.
    # Then T_i = G_i T_{i+1}. 
    # Wait, T_i(P) = (G_i ... GN) P (G_i ... GN)^\dagger.
    # So T_i = T_{i+1} o G_i ? No.
    # Let's verify composition order.
    # If we apply G then H, the total unitary is H G.
    # The tableau for H G should map P to (H G) P (H G)^\dagger = H (G P G^\dagger) H^\dagger.
    # So if T_G maps P to G P G^\dagger, and T_H maps Q to H Q H^\dagger.
    # Then T_{HG}(P) = T_H(T_G(P)).
    # So we apply maps in the same order as gates.
    # But we want the tableau of the *suffix*.
    # Suffix at i is G_{i+1} ... GN.
    # Let S_i be the tableau of G_{i+1} ... GN.
    # S_{N} = Identity.
    # S_{i-1} = Tableau(G_i ... GN) = Tableau(G_i) then S_i ?
    # Yes, we propagate through G_i then through rest.
    # So S_{i-1}(P) = S_i( G_i P G_i^\dagger ).
    # So we can build the tableau backwards.
    # S_{i-1} is S_i composed with G_i.
    
    # Wait, Stim's Tableau.prepend operation?
    # Or just track the tableau S. Initially Identity.
    # Loop i from N-1 down to 0.
    # Get gate G = ops[i].
    # For each qubit q in G:
    #   Check errors X, Z on q *after* G.
    #   Propagate them through S.
    #   Check weight.
    # Update S: S = S.prepend(G) ? 
    # Actually, S represents U_{suffix}.
    # We want new S' representing U_{suffix} G_i ? No, G_i U_{suffix} ? No.
    # The circuit is G1 ... GN.
    # Suffix at i is G_{i+1} ... GN.
    # Suffix at i-1 is G_i G_{i+1} ... GN.
    # So S_{i-1} = S_i * G_i (where * means G_i applied first).
    # In Stim, `tableau.do(gate)` applies gate to the tableau.
    # If tableau T represents U, and we do G, does it become U G or G U?
    # Simulating a circuit: start with I. Do G1 -> G1. Do G2 -> G2 G1.
    # So `do` appends to the *end* of the sequence.
    # So if we maintain a tableau T corresponding to "operations done so far",
    # we want to maintain the tableau of the *suffix*.
    # Suffix_i = G_{i+1} ... GN.
    # We want to add G_i to the *beginning* of Suffix_i.
    # Suffix_{i-1} = Suffix_i * G_i (applied first).
    # So if we have T representing U, and we want T' representing U G_i.
    # That is `T.prepend(G_i)`?
    # Stim doesn't have `prepend`.
    
    # Alternative:
    # Compute full tableau for the whole circuit? No, that's just global.
    # We can just simulate forward?
    # No, we need to propagate *from* the middle *to* the end.
    
    # Actually, Stim has `stim.Tableau.from_conjugated_generators`.
    # But maybe simpler:
    # Just iterate i from 0 to N.
    # Define `suffix = circuit[i+1:]`.
    # Compute `tableau = stim.Tableau.from_circuit(suffix)`.
    # This is O(N^2) if we do it for every gate.
    # With N gates, N ~ 1000? 1000^2 is 1M ops, totally fine.
    # Let's estimate gate count.
    
    print(f"Number of instructions: {len(circuit)}")
    
    # Let's count actual gates.
    count = 0
    for op in circuit:
        if op.name in ["CX", "H", "X", "Y", "Z", "I"]:
            # Stim ops can have multiple targets. e.g. CX 0 1 2 3
            # This counts as 1 op in the list, but multiple logical gates.
            # We need to split them or handle them.
            targets = op.targets_copy()
            if op.name == "CX":
                count += len(targets) // 2
            else:
                count += len(targets)
    print(f"Approximate gate count: {count}")
    
    # If count is small (< 5000), we can just do O(N^2).
    
    bad_count = 0
    
    # We'll re-read to get raw instructions to split them if needed?
    # Actually we can just process the circuit operations directly.
    # But we need to be careful about index i.
    
    # Let's build a flattened list of (gate, targets) to iterate over.
    flat_ops = []
    for op in circuit:
        if op.name == "CX":
            t = op.targets_copy()
            for k in range(0, len(t), 2):
                flat_ops.append( ("CX", [t[k], t[k+1]]) )
        elif op.name in ["H", "X", "Y", "Z", "I", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]:
            t = op.targets_copy()
            for k in t:
                flat_ops.append( (op.name, [k]) )
        else:
            # Maybe TICK or others. Ignore for faults but keep for circuit?
            # Wait, if we ignore them in flat_ops, we might mess up the suffix calculation if we reconstruct from flat_ops.
            # So we should preserve everything.
            flat_ops.append( (op.name, op.targets_copy()) )

    print(f"Flattened ops length: {len(flat_ops)}")
    
    # Actually, flattening might be complex if we want to run `stim.Circuit(suffix)`.
    # Better to just iterate through the original circuit and handle multi-target ops.
    # But then we can't easily "split" the circuit in the middle of a multi-target op.
    # We should normalize the circuit first: split multi-target ops into single ops.
    
    normalized_circuit = stim.Circuit()
    for op in circuit:
        print(f"DEBUG: op.name='{op.name}'")
        if op.name == "CX" or op.name == "CNOT":
            t = op.targets_copy()
            for k in range(0, len(t), 2):
                normalized_circuit.append("CX", [t[k], t[k+1]])
        elif op.name in ["H", "X", "Y", "Z", "I"]:
            t = op.targets_copy()
            for k in t:
                normalized_circuit.append(op.name, [k])
        else:
            normalized_circuit.append(op)
            
    print(f"Normalized circuit length: {len(normalized_circuit)}")
    
    # Now iterate
    for i in range(len(normalized_circuit)):
        op = normalized_circuit[i]
        # Only check faults for Clifford gates
        if op.name not in ["CX", "H", "X", "Y", "Z", "I"]:
            continue
            
        suffix = normalized_circuit[i+1:]
        # Compute tableau of suffix
        # Use simple simulation
        sim = stim.TableauSimulator()
        sim.do(suffix)
        # To get the propagation of error P, we can use `sim.peek_observable_expectation(P)`?
        # No, that measures.
        # We want P' = U P U^\dagger.
        # In Stim, `stim.Tableau.from_circuit(suffix)` gives the tableau T.
        # T(P) gives the propagated Pauli.
        # This is the most direct way.
        
        T = stim.Tableau.from_circuit(suffix)
        
        targets = [t.value for t in op.targets_copy()]
        
        # Check X and Z faults on each target
        for q in targets:
            for p_type in ["X", "Z"]:
                p = stim.PauliString(circuit.num_qubits)
                if p_type == "X":
                    p[q] = "X"
                else:
                    p[q] = "Z"
                
                res = T(p)
                w = res.weight
                
                if w >= threshold: # >= 4
                    # This is a bad fault
                    print(f"Bad fault at op {i} ({op}): {p_type} on {q} -> weight {w}")
                    bad_count += 1
                    if bad_count < 10:
                        print(f"  Result: {res}")

    print(f"Total bad faults: {bad_count}")

if __name__ == "__main__":
    find_bad_faults()
