import stim
import collections
import sys

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def analyze_faults_brute_force(circuit_file, stabilizers_file, threshold=3):
    c = load_circuit(circuit_file)
    # Estimate num_qubits
    num_qubits = c.num_qubits
    num_qubits = max(num_qubits, 63)
    
    # Load ops
    ops = []
    for instr in c:
        if instr.name in ['CX', 'SWAP', 'CZ', 'CY']:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append((instr.name, [targets[k].value, targets[k+1].value]))
        elif instr.name in ['H', 'S', 'X', 'Y', 'Z', 'I']:
            targets = instr.targets_copy()
            for t in targets:
                ops.append((instr.name, [t.value]))
                
    N = len(ops)
    print(f'Analyzing {N} operations with {num_qubits} qubits...')
    
    stabilizers = []
    with open(stabilizers_file, 'r') as f:
        for line in f:
            if line.strip():
                stabilizers.append(stim.PauliString(line.strip()))
    print(f'Loaded {len(stabilizers)} stabilizers.')
    
    # Create tableau for stabilizer check
    # Also simulate the circuit to get the actual output stabilizers
    # Ensure full size
    c_sim = c.copy()
    if num_qubits > c.num_qubits:
        c_sim.append("I", [num_qubits-1])
    sim_tableau = stim.Tableau.from_circuit(c_sim)
    
    try:
        stab_tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        inv_stab_tableau = stab_tableau.inverse()
        
        def is_stabilizer_strict(p):
            # Check if p is in the group of PROVIDED stabilizers
            try:
                p_mapped = inv_stab_tableau(p)
                s = str(p_mapped).replace('+', '').replace('-', '')
                if 'X' in s or 'Y' in s:
                    return False
                return True
            except:
                return False
                
        def is_stabilizer_of_circuit(p):
            # Check if p is stabilized by the circuit output
            # A Pauli P is stabilized by T if T^{-1}(P) is +Z_i (or product of Zs?)
            # No. T prepares state |0>. Output is T|0>.
            # Stabilizers of |0> are Z_i.
            # Stabilizers of T|0> are T Z_i T^{-1}.
            # So P is stabilizer iff P = T Z_i T^{-1} (or product).
            # <=> T^{-1} P T = Z_i (or product).
            # So apply inverse of sim_tableau to P. Check if result is only Z (and phase +1?)
            # Yes, phase must be +1.
            # If phase is -1, it is a stabilizer of -|psi>, i.e. P|psi> = -|psi>. Detected error.
            # If phase is +1, P|psi> = |psi>. Harmless.
            
            # Note: sim_tableau represents the unitary U.
            # The state is U|0>.
            # P is stabilizer of U|0> iff U^dag P U is stabilizer of |0>.
            # Stabilizers of |0> are operators M which are products of Zs (and I) with no -1 phase.
            # Actually, Z_i |0> = |0>. -Z_i |0> = -|0>.
            # So we check if U^dag P U consists of I, Z. And sign is +1.
            
            inv_sim = sim_tableau.inverse()
            p_mapped = inv_sim(p)
            s = str(p_mapped)
            if 'X' in s or 'Y' in s:
                return False
            # Check sign
            if s.startswith('-'):
                return False # Stabilizes -state (error)
            return True
            
    except Exception as e:
        print(f"Warning: Could not build tableau for stabilizer check: {e}")
        def is_stabilizer_strict(p): return False
        def is_stabilizer_of_circuit(p): return False

    dangerous_ops = collections.defaultdict(list)
    undetectable_dangerous = []
    
    # We do backward propagation
    # Initialize Tableau to Identity
    # Wait, t_suffix should be identity ON THE WHOLE set of qubits.
    t_suffix = stim.Tableau(num_qubits)
    
    # We need to simulate the circuit backward.
    # Stim's `Tableau` operations modify the tableau.
    # To represent the circuit *after* op i, we start with Identity (end of circuit) and apply ops in reverse.
    # But apply inverse ops? No, conjugate through the tableau.
    # t_suffix represents the channel from "after op i" to "end of circuit".
    # So if we have error E after op i, it becomes E' = t_suffix(E) at the end.
    # We want to check weight(E').
    
    # To update t_suffix:
    # If op is U, then the new channel (from before U) is U followed by t_suffix.
    # Channel(E) = t_suffix(U(E) U^dag)
    # So we update t_suffix by prepending U.
    # t_new = t_suffix.prepend(U)?
    # Stim doesn't have prepend. It has `then`.
    # `t_new = U.then(t_suffix)` ?
    # Let's check:
    #   Final = U2 U1
    #   t_suffix_2 = Identity
    #   t_suffix_1 = U2
    #   t_suffix_0 = U2 U1
    # Yes.
    
    # So we iterate backwards.
    # At step i (op U_i), we have t_suffix (product of U_{i+1}...U_N).
    # We check errors after U_i. E propagates through t_suffix.
    # Then we update t_suffix by prepending U_i.
    
    # In my previous code:
    # t_op_full = Tableau(U_i)
    # t_suffix = t_op_full.then(t_suffix)
    # This matches.
    
    for i in range(N-1, -1, -1):
        name, targs = ops[i]
        
        # Check faults after this op
        # Faults can be X, Y, Z on each target of the op.
        
        # We check errors on the qubits involved in the op?
        # Actually faults can happen anywhere, but usually we care about active locations.
        # "A fault is a location in the circuit where there is an unexpected disruption".
        # This usually means after each gate, on the qubits acted on.
        # But also idle qubits can have faults.
        # Let's focus on active qubits for now (the ones in targs).
        
        for q in targs:
            for p_char in ['X', 'Y', 'Z']:
                # Propagate P forward through t_suffix
                
                res = None
                if p_char == 'X':
                    res = t_suffix.x_output(q)
                elif p_char == 'Y':
                    res = t_suffix.y_output(q)
                elif p_char == 'Z':
                    res = t_suffix.z_output(q)
                    
                w = res.weight
                
                if w > threshold: # e.g. > 3 (so 4+)
                    # Strict stabilizer check (against PROVIDED stabilizers)
                    if is_stabilizer_strict(res):
                        is_stab = True
                    # Also check against CIRCUIT stabilizers (logical state)
                    elif is_stabilizer_of_circuit(res):
                        is_stab = True
                    else:
                        commutes_all = True
                        for stab in stabilizers:
                            if not stim.PauliString.commutes(res, stab):
                                commutes_all = False
                                break
                        
                        is_stab = False
                        
                    if not is_stab:
                        # It is a fault that propagates to > threshold and is not a stabilizer.
                        # It needs to be flagged.
                        dangerous_ops[i].append((q, p_char, w, commutes_all, res))
                        if commutes_all:
                            undetectable_dangerous.append((i, q, p_char, w, res))
        
        # Update tableau
        # Create a mini circuit for just this op
        full_mini = stim.Circuit()
        # Ensure size
        # We need to explicitly size the Tableau if we use from_circuit?
        # No, from_circuit determines size from circuit.
        # But we need to make sure it matches num_qubits.
        # So we add an Identity on the last qubit if needed.
        if num_qubits > 0:
            full_mini.append('I', [num_qubits-1]) 
            
        full_mini.append(name, targs)
        t_op_full = stim.Tableau.from_circuit(full_mini)
        
        # But wait, t_op_full will be size num_qubits (due to 'I' on num_qubits-1).
        # t_suffix is size num_qubits.
        t_suffix = t_op_full.then(t_suffix)
        
    print(f'Found {len(dangerous_ops)} locations with dangerous faults.')
    print(f'Found {len(undetectable_dangerous)} undetectable high-weight faults (Logical Errors).')
    
    count = 0
    print("Sample dangerous detectable faults (need flagging):")
    for k in sorted(dangerous_ops.keys()):
        v = dangerous_ops[k]
        for (q, p, w, comm, _) in v:
            if not comm:
                print(f"Op {k} ({ops[k]}): Fault {p} on {q} -> Weight {w}")
                count += 1
            if count > 10: break
        if count > 10: break
    
    return dangerous_ops, undetectable_dangerous

if __name__ == '__main__':
    circuit_file = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input_circuit.stim'
    stabs_file = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt'
    
    analyze_faults_brute_force(circuit_file, stabs_file, threshold=3)
