import stim
import collections

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def get_stabilizers():
    stabs_str = "IIIIXIIIIIXIIIXIXIXIIIIIXIIIIIIIIIIII, IIIIIXIIIIIIXIIXIIIXIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIXIIXXIIIIIIIIIXIIIII, IIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIXX, IIIXIIIIIIIIIIIIIIIIIIXXIIXIIXIIIIIIX, XIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIXXIII, IIIIIIIIIXIIIIIXIIIXIIIIIIIIXIIIIIIII, XIIIIIIIIIIIIIIIXIIIIIIIXIXIIXIIXIIII, IXXIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIII, IXXIIIIXXIIXIIIIIIIIIIIIIIIIIIIIIIXII, IIIIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXII, IIIIIIIIIIXIIIIIIXXIIXIIIIIIIIIIIIIII, XIIXIXXIIIIIXIIIIIIIIIIIIIIIIXIIIIIII, IIXIIIIIIIIXIXIIIIIIIIIIIIIIIIXIIIIII, IIIIIIIXIIIXIXIIIIIIIIXXIXIIIIIIIIIII, IIIIIIIXXIIIIIXIXIIIIIIXIIXIIIIIIIIII, IIIIIIIIIIIIIIIIIIXIIXIIXIIIIIIXXXIII, IIIXIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXX, IIIIZIIIIIZIIIZIZIZIIIIIZIIIIIIIIIIII, IIIIIZIIIIIIZIIZIIIZIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIZIIZZIIIIIIIIIZIIIII, IIIIIIIIIIIIIIIIIIIIIIZIIZIIIIIIIIIZZ, IIIZIIIIIIIIIIIIIIIIIIZZIIZIIZIIIIIIZ, ZIIIIIZIIIIIIIIIIIIIIIIIIIIIIIIIZZIII, IIIIIIIIIZIIIIIZIIIZIIIIIIIIZIIIIIIII, ZIIIIIIIIIIIIIIIZIIIIIIIZIZIIZIIZIIII, IZZIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIIII, IZZIIIIZZIIZIIIIIIIIIIIIIIIIIIIIIIZII, IIIIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZII, IIIIIIIIIIZIIIIIIZZIIZIIIIIIIIIIIIIII, ZIIZIZZIIIIIZIIIIIIIIIIIIIIIIZIIIIIII, IIZIIIIIIIIZIZIIIIIIIIIIIIIIIIZIIIIII, IIIIIIIZIIIZIZIIIIIIIIZZIZIIIIIIIIIII, IIIIIIIZZIIIIIZIZIIIIIIZIIZIIIIIIIIII, IIIIIIIIIIIIIIIIIIZIIZIIZIIIIIIZZZIII, IIIZIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZZ"
    return [stim.PauliString(s.strip()) for s in stabs_str.split(',')]

def get_error(circuit):
    flat_ops = list(circuit.flattened())
    
    # Run clean circuit history
    history = []
    sim = stim.TableauSimulator()
    # Force size to 37
    sim.do(stim.Circuit("I 36"))
    # Initial state (inverse tableau is identity)
    history.append(sim.current_inverse_tableau()) 
    
    for op in flat_ops:
        sim.do(op)
        history.append(sim.current_inverse_tableau())
        
    T_total = history[-1].inverse()
    
    bad_faults = []
    stabilizers = get_stabilizers()
    
    # Iterate ops
    for i, op in enumerate(flat_ops):
        # Identify targets (qubits only)
        targets = []
        for t in op.targets_copy():
            if t.is_qubit_target:
                targets.append(t.value)
        
        # We simulate faults occurring AFTER the operation
        # So we use history[i+1] which is the inverse tableau AFTER op i
        
        T_step = history[i+1]
        
        for q in targets:
            for pauli_char in ['X', 'Y', 'Z']:
                # Construct P_fault
                P_fault = stim.PauliString(37) # length 37
                P_fault[q] = pauli_char
                
                # Propagate
                P_input = T_step(P_fault)
                P_final = T_total(P_input)
                
                # Calculate weight
                s_rep = str(P_final)
                weight = len(s_rep) - s_rep.count('I') - 1
                
                if weight >= 3:
                    # Check stabilizers
                    detecting = []
                    for s_idx, stab in enumerate(stabilizers):
                        if not stab.commutes(P_final):
                            detecting.append(s_idx)
                    
                    intermediate_stab = None
                    if not detecting:
                        # Find intermediate stabilizer
                        # Iterate k from 0 to 36
                        # Generators of the stabilizer group are T_inv_prefix(Z_k)
                        
                        best_w = 999
                        for k in range(37):
                            Z_k = stim.PauliString(37)
                            Z_k[k] = 'Z'
                            S_k = T_step.inverse()(Z_k) # Wait. T_step is T_inv_prefix?
                            # sim.current_inverse_tableau() returns T^-1.
                            # So T_step = T_prefix^-1.
                            # Stabilizers are S = U Z U^-1.
                            # T_prefix^-1(P) = U P U^-1.
                            # So S_k = T_step(Z_k).
                            # Wait, T_step(P) maps output to input? Or input to output?
                            # sim.current_inverse_tableau() returns T^-1.
                            # If T maps input to output.
                            # T^-1 maps output to input?
                            # "Returns a tableau T such that T(P) = U^-1 P U".
                            # This maps P (at time t) to P' (at time 0).
                            # So S_k (at time t) is mapped to Z_k (at time 0).
                            # So S_k = T_step.inverse()(Z_k).
                            # Wait.
                            # S_k at time t should stabilize state |psi_t>.
                            # |psi_t> = U |0>.
                            # S_k |psi_t> = |psi_t>.
                            # U Z_k U^-1 U |0> = U Z_k |0> = U |0> = |psi_t>.
                            # So S_k = U Z_k U^-1.
                            # T_step(P) = U^-1 P U.
                            # So T_step(S_k) = U^-1 (U Z_k U^-1) U = Z_k.
                            # So S_k is such that T_step(S_k) = Z_k.
                            # So S_k = T_step.inverse()(Z_k).
                            # YES.
                            
                            S_k = T_step.inverse()(Z_k)
                            
                            if not S_k.commutes(P_fault):
                                # Found one!
                                w_s = sum(1 for p in range(37) if S_k[p] != 'I')
                                if w_s < best_w:
                                    best_w = w_s
                                    intermediate_stab = S_k
                                    
                    bad_faults.append({
                        'loc': i,
                        'qubit': q,
                        'pauli': pauli_char,
                        'weight': weight,
                        'detecting': detecting,
                        'intermediate': intermediate_stab
                    })
                    
    return bad_faults, stabilizers

if __name__ == "__main__":
    circuit = load_circuit("baseline.stim")
    bad_faults, stabilizers = get_error(circuit)
    
    critical_faults = [f for f in bad_faults if not f['detecting']]
    
    print(f"Total bad faults: {len(bad_faults)}")
    print(f"Critical faults: {len(critical_faults)}")
    
    if critical_faults:
        # Suggest intermediate checks
        # Group by S_k
        checks = []
        for f in critical_faults:
            if f['intermediate']:
                checks.append((f['loc'], str(f['intermediate'])))
            else:
                checks.append((f['loc'], "None"))
                
        # Unique checks
        unique_checks = sorted(list(set(checks)), key=lambda x: x[0])
        print(f"Suggest adding {len(unique_checks)} intermediate checks:")
        for loc, s in unique_checks[:20]:
            print(f"At loc {loc}: Check {s}")
