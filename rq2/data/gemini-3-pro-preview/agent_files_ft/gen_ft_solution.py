import json
import stim

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def anticommutes(p1, p2):
    anti_count = 0
    for q_idx_str, p_char in p1.items():
        q_idx = int(q_idx_str)
        if q_idx >= len(p2):
            continue
        stab_char = p2[q_idx]
        if p_char == 'I' or stab_char == 'I':
            continue
        if p_char == stab_char:
            continue
        anti_count += 1
    return (anti_count % 2) == 1

def generate(base_file, stab_file, json_file, output_file):
    with open(base_file, 'r') as f:
        base_circuit = f.read().strip()
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    stabilizers = parse_stabilizers(stab_file)
    errors = data.get('error_propagation', [])
    
    # Score stabilizers
    stab_scores = {s: 0 for s in stabilizers}
    for err in errors:
        final_paulis = err['final_paulis']
        for s in stabilizers:
            if anticommutes(final_paulis, s):
                stab_scores[s] += 1
    
    # Pick top stabilizers
    sorted_stabs = sorted(stab_scores.items(), key=lambda x: x[1], reverse=True)
    top_stabs = [s for s, score in sorted_stabs if score > 0]
    
    # Add checks
    # If no errors detected (e.g. first run of logic but no valid stabs?), pick some generic ones?
    # But here we have scores.
    # Let's take top 10 unique ones to be safe, or all that detect something.
    # The output circuit must be a string.
    
    # Check distinct stabilizers to avoid redundancy?
    # We can just add all that have score > 0, up to a limit.
    # Let's add top 5.
    
    selected_stabs = top_stabs[:5]
    
    print(f"Selected {len(selected_stabs)} stabilizers to check.")
    
    # Build circuit string
    new_circuit = base_circuit + "\n"
    
    ancilla_idx = 28 # Start after 0-27
    flag_qubits = []
    
    for s in selected_stabs:
        # Add check for s
        # s is a string of length 28
        # We need to measure it.
        # Format: H anc; CNOTs; H anc; M anc.
        
        # Determine check type.
        # If S contains X, we use CX ancilla target.
        # If S contains Z, we use CX target ancilla.
        # If mixed? We can do basis change on data? No, that disturbs data state?
        # Standard graph state stabilizers are usually uniform (all X or all Z) or specific.
        # The provided stabilizers are X...X or Z...Z or mixed?
        # "ZIZIZIZ..." -> Mixed? No, Z and I.
        # "XIXIXIX..." -> X and I.
        # "ZZIIZZ..." -> Z and I.
        # "XXIIXX..." -> X and I.
        # It seems they are Pauli strings with I.
        # Are there any Y?
        # The list has X... and Z...
        # Wait, let's check `stabilizers_prompt.txt`.
        # All chars are X, Z, I. No Y.
        # And they don't seem to mix X and Z in the same stabilizer.
        # e.g. "XXII..." all X. "ZZII..." all Z.
        # So we can just assume X-type or Z-type.
        
        is_x_type = 'X' in s
        is_z_type = 'Z' in s
        
        if is_x_type and is_z_type:
            # Mixed X and Z.
            # "All ancilla qubits must be initialized in |0>..."
            # To measure X_i Z_j:
            # Ancilla A.
            # H A.
            # For X_i: CX A i.
            # For Z_j: CX j A.
            # H A.
            # M A.
            pass
        
        flag_qubit = ancilla_idx
        flag_qubits.append(flag_qubit)
        ancilla_idx += 1
        
        # Append instructions
        # Use single line for H
        new_circuit += f"H {flag_qubit}\n"
        
        # CNOTs
        cnot_ops = []
        for q_idx, char in enumerate(s):
            if char == 'X':
                # Measure X: H A, CX A Q, H A (measures X of Q -> Z of A)
                # Wait. Standard parity check:
                # Check operator P = X_q.
                # We want to measure eigenvalue of P.
                # Circuit: Prepare A in +, apply Control-P (A controls P on system). Measure A in X.
                # Control-X is CNOT (A control, Q target).
                # Measure A in X (H then M).
                # Correct.
                cnot_ops.append(f"CX {flag_qubit} {q_idx}")
            elif char == 'Z':
                # Check operator P = Z_q.
                # Control-Z is CZ (A control, Q target).
                # Or CNOT (Q control, A target).
                # If we use CNOT(Q, A):
                # If Q is |1> (Z=-1), A flips.
                # If Q is |0> (Z=+1), A stays.
                # So Z of A becomes Z_A * Z_Q.
                # Measuring A in X basis?
                # No. CNOT(Q, A) copies Z of Q to X of A?
                # Let's trace:
                # A in +, Q arbitrary.
                # CX Q A:
                # |+>|0> -> |+>|0>
                # |+>|1> -> |+>|1> (Wait, CX(1,0) -> 1,1. CX(1,1) -> 1,0. |+> = 0+1. 0->0, 1->1? No.
                # Let's use Hadamard test logic.
                # We want to measure Z.
                # Use CZ(A, Q).
                # Stim has CZ.
                # But typically we prefer CNOT.
                # CZ(A, Q) = H(Q) CX(A, Q) H(Q) ? No.
                # CZ(A, Q) is symmetric.
                # CNOT(Q, A) is related.
                # Let's just use `CX` as Stim supports it.
                # For Z check: `CX Q A`. (Q control, A target).
                # If Q is 1, A flips X.
                # Measure A in X basis?
                # Initial A: |0> -> H -> |+>.
                # If flipped (X applied): |+> -> |+>. No. X|+> = |+>.
                # Wait. X|+> = |+>. X|-> = -|->.
                # So `CX Q A` does NOT copy Z info to phase of A?
                # `CX Q A`:
                # |0>_Q |+>_A -> |0> |+>
                # |1>_Q |+>_A -> |1> X|+> = |1> |+>.
                # No kickback.
                # To get kickback (phase flip on A), we need target to be |->.
                # Initial A |0> -> H -> |+>.
                # We want Z check.
                # We need `CZ A Q`.
                # If we use `CX`, we can use `CX A Q` surrounded by H on Q? No, don't touch Q basis.
                # `CX Q A` with A in |->?
                # No, we start A in |0>.
                # If we do `H A`. Then `CZ A Q`. Then `H A`.
                # `CZ` is available.
                # Does `CZ` work?
                # `CZ 0 1` in Stim.
                # Yes.
                # Can I use `CX`?
                # `CZ(c,t)` is equivalent to `H(t) CX(c,t) H(t)`.
                # I prefer not to add H on data qubits if I can avoid it (structure).
                # But `CZ` is a primitive.
                # Is `CZ` allowed? "described in Stim format". Stim supports CZ.
                # But does the *hardware* support it? The prompt doesn't say.
                # Assuming Stim gates are allowed.
                # Using CZ is safer for Z checks.
                # Or I can use `CX` with correct basis.
                # For Z check, we check Z parity.
                # A in |+>.
                # `CZ A Q` for each Q.
                # `H A`. `M A`.
                # This measures Z...Z.
                # Correct.
                # So for Z: use `CZ flag_qubit q_idx`.
                # For X: use `CX flag_qubit q_idx`. (A control, Q target).
                # Is that right?
                # Check X parity:
                # `CX A Q`.
                # A in |+>.
                # If Q is in Z eigenstate? No, check X.
                # `CX A Q`: Propagates X from A to Q?
                # No, we want to measure X of Q.
                # X of Q propagates to Z of A? No.
                # Z of Q propagates to Z of A?
                # `CX A Q`:
                # |+>_A |0>_Q -> |00> + |11> (Bell state).
                # This is getting confusing.
                # Standard Parity Check:
                # Measure Z operator: `H(A)`, `CNOT(Q, A)`, `H(A)`? No.
                # To measure Z: `H(A)`, `CZ(A,Q)`, `H(A)`.
                # To measure X: `H(A)`, `CNOT(A,Q)`, `H(A)`.
                # Let's verify `CNOT(A,Q)` for X measurement.
                # We want to measure eigenvalue of X_Q.
                # Operator C_X = CNOT(A,Q).
                # P = X_Q.
                # Does A control P?
                # If A=1, apply X to Q.
                # Yes, CNOT(A,Q) is "Controlled-X".
                # So if we prepare A in |+>, apply Controlled-X, measure A in X, we measure X eigenvalue?
                # Yes. Hadamard test for unitary U=X.
                # Re( <psi| U |psi> ).
                # If |psi> is X eigenstate with ev +1: X|psi>=|psi>. Controlled-X acts as I on A. A stays |+>. M gives 0.
                # If |psi> is X eigenstate with ev -1: X|psi>=-|psi>. Controlled-X adds phase -1 if A=1. A becomes |->. M gives 1.
                # Correct.
                # So:
                # X check: `CX flag q`.
                # Z check: `CZ flag q`.
                
                # But does `stim` have `CZ`? Yes.
                # The input circuit uses `CX` and `H`.
                # Maybe I should stick to `CX`?
                # `CZ i j` is valid stim.
                # I'll use `CZ`.
                
                if char == 'X':
                    cnot_ops.append(f"CX {flag_qubit} {q_idx}")
                elif char == 'Z':
                    cnot_ops.append(f"CZ {flag_qubit} {q_idx}")
        
        # Add ops
        if cnot_ops:
            new_circuit += " ".join(cnot_ops) + "\n"
        
        # Final H and M
        new_circuit += f"H {flag_qubit}\nM {flag_qubit}\n"

    with open(output_file, 'w') as f:
        f.write(new_circuit)
    
    print(json.dumps(flag_qubits))

if __name__ == "__main__":
    import sys
    generate(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
