import stim
import sys

def get_stabilizers():
    with open("stabilizers_d21.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = 0
    failed_indices = []
    for i, s_str in enumerate(stabilizers):
        pauli = stim.PauliString(s_str)
        if sim.peek_observable_expectation(pauli) == 1:
            preserved += 1
        else:
            failed_indices.append(i)
    return preserved, len(stabilizers), failed_indices

def analyze_faults(circuit, data_qubits, flag_qubits):
    num_qubits = circuit.num_qubits
    # Ensure num_qubits covers all used qubits
    max_q = 0
    for op in circuit.flattened():
        for t in op.targets_copy():
            if t.is_qubit_target:
                max_q = max(max_q, t.value)
    
    # We might have added ancillas, so num_qubits might be larger than original
    sim_size = max(max_q + 1, max(data_qubits) + 1 if data_qubits else 0, max(flag_qubits) + 1 if flag_qubits else 0)
    
    # Propagator from "current time" to "end of circuit"
    # Initially identity
    prop = stim.Tableau(sim_size)
    
    ops = list(circuit.flattened())
    bad_faults = []
    threshold = 10 # d=21 -> t=10
    
    # Iterate backwards
    # We want to insert error AFTER op[i].
    # So initially prop is empty (after last op).
    # Then we prepend op[N-1], then verify faults after op[N-2] (which propagate through op[N-1]).
    # Wait.
    # Faults can occur:
    # 1. Before the circuit starts (state prep errors). Usually ignored or considered as faults before first gate.
    # 2. After each gate.
    
    # Let's consider faults after each gate.
    # Including after the last gate.
    
    # Loop i from len(ops) down to -1?
    # -1 means before first gate.
    # len(ops)-1 means after last gate.
    
    # The prompt says: "For each location l in spots(C)... C[l <- P]"
    # "spots(C) be the set of valid fault locations".
    # Usually this means after every operation on the qubits involved.
    
    # We will iterate backwards.
    # Start with prop = Identity. This corresponds to faults after the last gate.
    
    total_faults_checked = 0
    
    for i in range(len(ops) - 1, -2, -1):
        # Time step i. 
        # i = len(ops)-1: after last gate.
        # i = -1: before first gate.
        
        # Determine active qubits at this time step.
        # If i >= 0, active qubits are targets of ops[i].
        # If i == -1, active qubits are all qubits (initialization faults).
        
        active_qubits = set()
        if i >= 0:
            op = ops[i]
            for t in op.targets_copy():
                if t.is_qubit_target:
                    active_qubits.add(t.value)
        else:
            # Before first gate, any qubit could have a fault (prep error)
            # Or maybe we limit to those used in the first gate?
            # Typically "locations" are associated with gates.
            # Let's stick to "after each gate".
            pass

        # If i < 0, we stop?
        # Standard analysis usually places faults on the output of each gate.
        if i < 0:
            break

        # Check faults on active qubits
        for q in active_qubits:
            for p_type in ['X', 'Y', 'Z']:
                total_faults_checked += 1
                
                # Propagate P through `prop`
                if p_type == 'X':
                    p_final = prop.x_output(q)
                elif p_type == 'Z':
                    p_final = prop.z_output(q)
                elif p_type == 'Y':
                    # Y = iXZ. Phase doesn't matter for weight.
                    px = prop.x_output(q)
                    pz = prop.z_output(q)
                    p_final = px * pz 
                
                # Calculate weight on data qubits
                data_weight = 0
                triggered = False
                
                # We can iterate through the Pauli string.
                # Since iterating python-side is slow for large strings,
                # but we only care about specific indices.
                
                # Optimize: `p_final` is a stim.PauliString.
                # We can access elements.
                
                # Check flags first (fail fast?)
                # Flag triggers if X error (Pauli=1)
                for fq in flag_qubits:
                    if fq < len(p_final):
                        if p_final[fq] == 1: # 1=X
                            triggered = True
                            break # Flag triggered, safe.
                
                if triggered:
                    continue
                
                # If not triggered, check weight
                for dq in data_qubits:
                    if dq < len(p_final):
                        if p_final[dq] != 0: # 0=I
                            data_weight += 1
                            if data_weight > threshold:
                                break
                
                if data_weight > threshold:
                    bad_faults.append( (i, q, p_type, data_weight) )
        
        # Update prop by prepending the current gate ops[i]
        op = ops[i]
        
        name = op.name
        targets = [t.value for t in op.targets_copy()]
        
        arity = 1
        if name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP"]:
            arity = 2
        
        # Split targets into chunks
        for k in range(0, len(targets), arity):
            sub_targets = targets[k:k+arity]
            gate_tableau = stim.Tableau.from_named_gate(name)
            prop.prepend(gate_tableau, sub_targets)

    return bad_faults, total_faults_checked

if __name__ == "__main__":
    with open("circuit_d21.stim", "r") as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    # Identify data qubits and flag qubits
    # For now, all used qubits are data, no flags.
    used_qubits = set()
    for op in circuit.flattened():
        for t in op.targets_copy():
            if t.is_qubit_target:
                used_qubits.add(t.value)
    
    # Assuming no flags yet
    data_qubits = sorted(list(used_qubits))
    flag_qubits = []
    
    # If we modify the circuit to add flags, we need to distinguish them.
    # The prompt says input circuit has 115 qubits.
    # We will treat 0-114 as data.
    # Any qubit >= 115 will be treated as flag.
    
    data_qubits = [q for q in used_qubits if q <= 114]
    flag_qubits = [q for q in used_qubits if q > 114]
    
    print(f"Data qubits: {len(data_qubits)}")
    print(f"Flag qubits: {len(flag_qubits)}")
    
    stabilizers = get_stabilizers()
    preserved, total, failed = check_stabilizers(circuit, stabilizers)
    print(f"Stabilizers preserved: {preserved}/{total}")
    if failed:
        print(f"Failed indices: {failed[:10]}...")
    
    bad_faults, checked = analyze_faults(circuit, data_qubits, flag_qubits)
    print(f"Checked {checked} faults.")
    print(f"Bad faults count: {len(bad_faults)}")
    
    if bad_faults:
        print("Example bad faults:")
        for i, q, p, w in bad_faults[:5]:
            print(f"  Gate {i}, Qubit {q}, Pauli {p}, Weight {w}")

