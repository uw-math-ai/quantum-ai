import stim
import sys

def analyze(circuit_path):
    with open(circuit_path, 'r') as f:
        circuit = stim.Circuit(f.read())

    # 1. Simulate perfect circuit to get final state stabilizers
    sim = stim.TableauSimulator()
    sim.do(circuit)
    # Save the state (we can peek into it)
    # Actually we need to restart for each check? No, peek is non-destructive.
    
    # 2. Identify ops and locations
    ops = []
    for instr in circuit.flattened():
        name = instr.name
        targets = instr.targets_copy()
        if name in ["CX", "SWAP", "CZ", "ISWAP"]:
             for k in range(0, len(targets), 2):
                 t1 = targets[k].value
                 t2 = targets[k+1].value
                 ops.append((name, [t1, t2]))
        elif name in ["H", "S", "X", "Y", "Z", "I"]:
             for t in targets:
                 ops.append((name, [t.value]))
        else:
             pass # Measurements are not faults locations usually (or readouts)
             
    # 3. Backward propagation of faults
    num_qubits = sim.num_qubits # Automatically sized
    t_rem = stim.Tableau(num_qubits)
    
    data_indices = set(range(49))
    flag_indices = set(range(49, num_qubits))
    THRESHOLD = 4
    
    bad_faults = []
    
    for k in range(len(ops)-1, -1, -1):
        name, targs = ops[k]
        
        for q in targs:
            for p_type in [1, 3]: # X, Z
                ps = stim.PauliString(num_qubits)
                ps[q] = p_type 
                final_ps = t_rem(ps)
                
                # Check if stabilizer
                # We check expectation against the PERFECT state
                if sim.peek_observable_expectation(final_ps) != 0:
                    # Stabilizer (or -Stabilizer). Trivial.
                    continue
                
                # Non-trivial error
                w_data = 0
                is_flagged = False
                for i in range(num_qubits):
                    p = final_ps[i]
                    if p != 0:
                        if i in data_indices:
                            w_data += 1
                        elif i in flag_indices:
                            if p == 1: # X on flag
                                is_flagged = True
                
                if w_data >= THRESHOLD and not is_flagged:
                    bad_faults.append({
                        'loc': k,
                        'weight': w_data
                    })
        
        # Update T_rem
        mini_c = stim.Circuit()
        if num_qubits > 0: mini_c.append("I", [num_qubits-1])
        mini_c.append(name, targs)
        t_rem = stim.Tableau.from_circuit(mini_c).then(t_rem)

    print(f"Found {len(bad_faults)} bad faults.")

if __name__ == "__main__":
    analyze(sys.argv[1] if len(sys.argv)>1 else "candidate_fixed_v3.stim")
