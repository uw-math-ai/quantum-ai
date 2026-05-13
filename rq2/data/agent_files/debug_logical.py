import stim

circuit_str = """CX 15 0 0 15 15 0
H 7
CX 7 0 11 0 16 0 5 1 1 5 5 1
H 1 2 3 4 6 15
CX 1 2 1 3 1 4 1 6 1 7 1 13 1 15 1 16 7 2 2 7 7 2 2 7 2 11 2 16 3 2 7 3 3 7 7 3 3 10 3 16 4 6 4 7 4 11 4 12 4 13 4 15 15 5 5 15 15 5
H 15
CX 5 6 5 8 5 12 5 15 7 6 6 7 7 6 6 12 6 16 10 7 7 10 10 7 7 12 11 7 15 8 8 15 15 8 8 9 8 12 8 14 10 8 10 9 9 10 10 9 9 10 9 12 9 15 10 12 10 13 11 10 12 10 13 10 14 10 16 10 14 11 11 14 14 11 11 12 11 15 13 11 15 12 12 15 15 12 13 12 15 13 13 15 15 13 14 13 16 13 16 14"""

stabilizers = [
    "IIIIIXIIIXIXXIIII", "IIIIIIIIXIXIIXIXI", "IIIXIIIXIIIIIIXIX", "IIXIIIXIIIIIIIXIX", 
    "IIIIXXXXXIXXIIIIX", "IXIIXIIIIIXIIXIII", "IIIIIIIIXXIXIIIXI", "XIXXIIIIIIIIIIXII", 
    "IIIIIZIIIZIZZIIII", "IIIIIIIIZIZIIZIZI", "IIIZIIIZIIIIIIZIZ", "IIZIIIZIIIIIIIZIZ", "IIIIZZZZZIZZIIIIZ", "IZIIZIIIIIZIIZIII", "IIIIIIIIZZIZIIIZI", "ZIZZIIIIIIIIIIZII"
]

def analyze_trace():
    c = stim.Circuit(circuit_str)
    flat_ops = []
    for instr in c:
        if instr.name in ["CX", "H", "S", "X", "Y", "Z"]:
            targets = instr.targets_copy()
            if instr.name == "CX":
                for i in range(0, len(targets), 2):
                    flat_ops.append(("CX", targets[i].value, targets[i+1].value))
            else:
                for t in targets:
                    flat_ops.append((instr.name, t.value))
    
    # Identify the two logical errors (Op 6 and Op 38 from previous run)
    targets_to_trace = [
        {"op_idx": 6, "qubit": 16, "error": "Z"},
        {"op_idx": 38, "qubit": 4, "error": "X"}
    ]
    
    # We want to check for intermediate stabilizers.
    # At each step k > op_idx, the error E evolves to E_k.
    # The stabilizers also evolve! S evolves to S_k.
    # Actually, we define the code by the FINAL stabilizers.
    # So the "instantaneous stabilizers" at step k are S_k such that S_final = U_{k->end} * S_k * U_{k->end}^dagger.
    # So S_k = U_{k->end}^dagger * S_final * U_{k->end}.
    # We want to check if E_k anticommutes with any S_k.
    # Equivalently, does E_final anticommute with S_final?
    # NO. We already know E_final commutes with ALL S_final (that's why it's logical).
    # So E_final commutes with S_final implies E_k commutes with S_k.
    # So we CANNOT detect it by checking stabilizers of the code *at that moment*.
    
    # Wait, "checking intermediate stabilizers" works if the code *structure* changes or if we have *other* checks.
    # But here we are just preparing the state.
    # If the error is logical, it means at the moment of creation it was undetectable?
    # Or it became logical.
    # A logical error is an error that commutes with stabilizers.
    # If it commutes at the end, it commutes everywhere (algebraically).
    
    # So I cannot detect these logical errors using the *code* stabilizers.
    # I must use *ancilla flags* to catch the specific fault event.
    
    # Run ideal simulation to get the state
    sim = stim.TableauSimulator()
    sim.do(c)
    
    print("Checking if logical errors are benign (stabilize the state):")
    # For the 2 logical errors found previously
    # We need to reconstruct them exactly.
    # Op 6: CX 16 0. Z on 16.
    # Op 38: CX 4 11. X on 4.
    
    # We need the full Pauli string for them.
    # I'll just re-run the propagation logic for these two.
    
    # Re-run analysis for just these 2 ops
    # Copy-paste logic from analyze_circuit_v2 somewhat
    
    # Actually, simpler: just inject them and see.
    # But I need the final Pauli string.
    
    # ... (skipping full re-implementation, I will just assume I can use the previous output)
    # But wait, I need to know if they are X_L or Z_L.
    # I can just use the script to check expectation.
    
    bad_ops = [
        (6, 16, 'Z'),
        (38, 4, 'X')
    ]
    
    for op_idx, q, p_char in bad_ops:
        # Construct suffix
        suffix = stim.Circuit()
        suffix.append("I", [16])
        op_counter = 0
        suffix_start_idx = op_idx + 1
        
        # Extract suffix from c
        current_idx = 0
        for instr in c:
            if instr.name in ["CX", "H", "S", "X", "Y", "Z"]:
                targets = instr.targets_copy()
                if instr.name == "CX":
                    for i in range(0, len(targets), 2):
                        if current_idx >= suffix_start_idx:
                             suffix.append("CX", [targets[i].value, targets[i+1].value])
                        current_idx += 1
                else:
                    for t in targets:
                        if current_idx >= suffix_start_idx:
                            suffix.append(instr.name, [t.value])
                        current_idx += 1
            else:
                pass
        
        # Propagate error
        t = stim.Tableau.from_circuit(suffix)
        ps = stim.PauliString(17)
        ps[q] = p_char
        final_ps = t(ps)
        
        # Check expectation on ideal state
        expectation = sim.peek_observable_expectation(final_ps)
        print(f"Op {op_idx} q{q}={p_char} -> Expectation: {expectation}")
        if abs(expectation) > 0.9:
            print("  -> Benign (Stabilizer/Global Phase)")
        else:
            print("  -> Harmful (Logical Error)")


if __name__ == "__main__":
    analyze_trace()
