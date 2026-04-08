import stim
import collections

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def get_stabilizers():
    stabs_str = "IIIIXIIIIIXIIIXIXIXIIIIIXIIIIIIIIIIII, IIIIIXIIIIIIXIIXIIIXIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIXIIXXIIIIIIIIIXIIIII, IIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIXX, IIIXIIIIIIIIIIIIIIIIIIXXIIXIIXIIIIIIX, XIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIXXIII, IIIIIIIIIXIIIIIXIIIXIIIIIIIIXIIIIIIII, XIIIIIIIIIIIIIIIXIIIIIIIXIXIIXIIXIIII, IXXIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIII, IXXIIIIXXIIXIIIIIIIIIIIIIIIIIIIIIIXII, IIIIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXII, IIIIIIIIIIXIIIIIIXXIIXIIIIIIIIIIIIIII, XIIXIXXIIIIIXIIIIIIIIIIIIIIIIXIIIIIII, IIXIIIIIIIIXIXIIIIIIIIIIIIIIIIXIIIIII, IIIIIIIXIIIXIXIIIIIIIIXXIXIIIIIIIIIII, IIIIIIIXXIIIIIXIXIIIIIIXIIXIIIIIIIIII, IIIIIIIIIIIIIIIIIIXIIXIIXIIIIIIXXXIII, IIIXIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXX, IIIIZIIIIIZIIIZIZIZIIIIIZIIIIIIIIIIII, IIIIIZIIIIIIZIIZIIIZIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIZIIZZIIIIIIIIIZIIIII, IIIIIIIIIIIIIIIIIIIIIIZIIZIIIIIIIIIZZ, IIIZIIIIIIIIIIIIIIIIIIZZIIZIIZIIIIIIZ, ZIIIIIZIIIIIIIIIIIIIIIIIIIIIIIIIZZIII, IIIIIIIIIZIIIIIZIIIZIIIIIIIIZIIIIIIII, ZIIIIIIIIIIIIIIIZIIIIIIIZIZIIZIIZIIII, IZZIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIIII, IZZIIIIZZIIZIIIIIIIIIIIIIIIIIIIIIIZII, IIIIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZII, IIIIIIIIIIZIIIIIIZZIIZIIIIIIIIIIIIIII, ZIIZIZZIIIIIZIIIIIIIIIIIIIIIIZIIIIIII, IIZIIIIIIIIZIZIIIIIIIIIIIIIIIIZIIIIII, IIIIIIIZIIIZIZIIIIIIIIZZIZIIIIIIIIIII, IIIIIIIZZIIIIIZIZIIIIIIZIIZIIIIIIIIII, IIIIIIIIIIIIIIIIIIZIIZIIZIIIIIIZZZIII, IIIZIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZZ"
    return [stim.PauliString(s.strip()) for s in stabs_str.split(',')]

def get_error(circuit, fault_loc, fault_pauli_str, target_qubit):
    # Construct faulty circuit
    # Since we can't easily insert into flattened, we iterate and rebuild
    # Or simply: split circuit at instruction index
    
    # Wait, stim flattened iteration yields instructions.
    # We can rebuild the circuit.
    
    # Actually, stim Circuit has `copy()`?
    # We can build a new circuit by appending.
    
    # Better:
    # `sim = stim.TableauSimulator()`
    # `sim.do(circuit)` -> clean state
    # `sim_fault = stim.TableauSimulator()`
    # Iterate instructions. At `fault_loc`, apply instruction, then apply fault.
    
    # We need to know which qubit indices are involved in the instruction at `fault_loc`?
    # No, the fault iteration iterates over (loc, qubit, pauli).
    
    # Let's map flattened index to instructions.
    
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
        # P_fault is in the frame after op i
        # We want to map it to the end frame
        
        # Transform map M = T_total * history[i+1]
        # P_final = T_total( history[i+1](P_fault) )
        
        T_step = history[i+1]
        
        for q in targets:
            for pauli_char in ['X', 'Y', 'Z']:
                # Construct P_fault
                # It's a single qubit Pauli.
                P_fault = stim.PauliString(37) # length 37
                P_fault[q] = pauli_char
                
                # Propagate
                # First map back to input
                P_input = T_step(P_fault)
                # Then map forward to output
                P_final = T_total(P_input)
                
                # Calculate weight (ignore identity)
                weight = 0
                # Efficient weight counting?
                # String representation has I, X, Y, Z
                # Convert to string and count non-Is
                # Or iterating indices.
                # PauliString is not directly iterable for chars?
                # It has .to_numpy()?
                # Or just string conversion.
                s_rep = str(P_final)
                # s_rep starts with + or -
                weight = len(s_rep) - s_rep.count('I') - 1 # -1 for sign
                
                if weight >= 3:
                    # Check stabilizers
                    detecting = []
                    for s_idx, stab in enumerate(stabilizers):
                        if not stab.commutes(P_final):
                            detecting.append(s_idx)
                    
                    bad_faults.append({
                        'loc': i,
                        'qubit': q,
                        'pauli': pauli_char,
                        'weight': weight,
                        'detecting': detecting
                    })
                    
    return bad_faults, stabilizers

if __name__ == "__main__":
    circuit = load_circuit("baseline.stim")
    bad_faults, stabilizers = get_error(circuit, 0, "", 0)
    
    print(f"Total bad faults: {len(bad_faults)}")
    
    # Greedy set cover
    uncovered = set(range(len(bad_faults)))
    selected_stabilizers = []
    
    while uncovered:
        # Find stabilizer that covers most uncovered faults
        counts = collections.Counter()
        for f_idx in uncovered:
            for s_idx in bad_faults[f_idx]['detecting']:
                counts[s_idx] += 1
        
        if not counts:
            print("Remaining faults cannot be covered!")
            # Print example
            f_idx = list(uncovered)[0]
            print(f"Fault {bad_faults[f_idx]}")
            break
            
        best_s = counts.most_common(1)[0][0]
        selected_stabilizers.append(best_s)
        
        # Remove covered
        new_uncovered = set()
        for f_idx in uncovered:
            if best_s not in bad_faults[f_idx]['detecting']:
                new_uncovered.add(f_idx)
        uncovered = new_uncovered
        
    print(f"Selected {len(selected_stabilizers)} stabilizers: {selected_stabilizers}")
    
    # Print selected stabilizer strings
    for s_idx in selected_stabilizers:
        print(f"S{s_idx}: {stabilizers[s_idx]}")

