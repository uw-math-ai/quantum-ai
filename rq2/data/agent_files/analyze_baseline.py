import stim
import sys

def get_stabilizers():
    with open('stabilizers_d9_input.txt', 'r') as f:
        return [stim.PauliString(line.strip()) for line in f if line.strip()]

def get_circuit():
    with open('circuit_d9_input.stim', 'r') as f:
        return stim.Circuit.from_file(f)

def analyze():
    circuit = get_circuit()
    stabilizers = get_stabilizers()
    
    data_qubits = set()
    for s in stabilizers:
        for i, p in enumerate(s):
            if p != 0:
                data_qubits.add(i)
    
    print(f"Num data qubits: {len(data_qubits)}")
    
    # Compute total unitary
    print("Computing total unitary...")
    total_tableau = stim.Tableau.from_circuit(circuit)
    
    # We will iterate forward and track the prefix tableau
    prefix_tableau = stim.Tableau(circuit.num_qubits) # Identity
    
    bad_faults = []
    
    print("Analyzing faults...")
    
    # Iterate over operations
    # Note: Circuit iteration yields instructions.
    # We only care about faults after Clifford gates.
    # We assume single qubit Pauli faults can occur at any location.
    # Locations are: before the circuit, and after each gate.
    # Actually, usually "locations" means "after each gate".
    # And "input" locations (before any gate).
    
    # To be precise, let's inject errors after every gate.
    
    # Optimization: precompute inverses?
    # No, we update prefix_tableau incrementally.
    # We need U_suffix = U_total * U_prefix^-1
    # U_suffix * U_prefix = U_total
    # So error E at current location propagates to U_suffix(E).
    
    # Actually, we can just maintain U_suffix.
    # Start with U_suffix = U_total.
    # When we pass a gate G, we are effectively removing it from the start of the remaining circuit.
    # So U_suffix_new = U_suffix_old * G^-1.
    # Let's verify:
    # U_suffix_old corresponds to (G then Rest).
    # U_suffix_old = Rest * G.
    # We want Rest.
    # Rest = U_suffix_old * G^-1.
    # Yes.
    
    current_suffix = total_tableau.copy()
    
    threshold = 4
    
    gates_processed = 0
    bad_faults = []

    # Get instructions
    # Note: iterating directly yields instructions
    instructions = list(circuit)
    
    # We want to iterate forward, removing gates from the start of the remaining circuit.
    # Current suffix S_0 = G_N ... G_1
    # After processing G_1, we want S_1 = G_N ... G_2
    # S_1 = S_0 * G_1^-1 (operator multiplication, applies G_1^-1 first)
    # tableau.then(other) means apply tableau, then other.
    # Corresponds to other * tableau.
    # We want S_1 = S_0 composed with G_1^-1 on the right (input side)?
    # No. S_1(P) = S_0(G_1^{-1}(P)).
    # So apply G_1^{-1}, then S_0.
    # So S_1 = G_1_inv.then(S_0).
    
    for i, instruction in enumerate(instructions):
        # Check faults *before* this gate (between previous and current)
        # We only check faults on the qubits involved in this gate to save time,
        # plus maybe neighbors? For now, just targets.
        
        targets = []
        # Only check Clifford gates
        if instruction.name in ['CX', 'H', 'S', 'S_DAG', 'X', 'Y', 'Z', 'I', 'C_XYZ', 'C_ZYX', 'SQRT_X', 'SQRT_X_DAG', 'SQRT_Y', 'SQRT_Y_DAG', 'SQRT_Z', 'SQRT_Z_DAG']:
            for t in instruction.targets_copy():
                if t.is_qubit_target:
                    targets.append(t.value)
        
        # Check faults
        # We assume faults are X/Z. Y is covered.
        for q in targets:
            # Check X and Z
            for p_type in ['X', 'Z']:
                # Construct Pauli
                # Since we are checking P *before* the gate G_i,
                # we just propagate P through current_suffix S_{i-1}.
                
                # Pauli P
                p = stim.PauliString(circuit.num_qubits)
                if p_type == 'X': p[q] = 1
                if p_type == 'Z': p[q] = 3
                
                # Propagate
                res = current_suffix(p)
                
                # Check weight on data qubits
                w = sum(1 for k in data_qubits if res[k] != 0)
                
                if w > threshold:
                    # Check if stabilized
                    detected = False
                    # Optimization: check commutation with stabilizers
                    # If it anticommutes with ANY, it is detected.
                    # We can pick *one* stabilizer to detect it.
                    # Ideally the cheapest one.
                    # But for now just checking existence.
                    for s in stabilizers:
                        if not s.commutes(res):
                            detected = True
                            break
                    
                    if not detected:
                        bad_faults.append(f"Fault after gate {i} ({instruction.name}) on qubit {q} type {p_type} -> weight {w}")

        # Update suffix
        # Remove instruction from start
        # S_{i} = G_i^{-1} * S_{i-1}
        # In Stim: S_i = G_i_inv_tableau.then(S_{i-1})
        
        # Construct inverse gate circuit
        inv_name = None
        if instruction.name == 'CX': inv_name = 'CX'
        elif instruction.name == 'H': inv_name = 'H'
        elif instruction.name == 'S': inv_name = 'S_DAG'
        elif instruction.name == 'S_DAG': inv_name = 'S'
        elif instruction.name == 'X': inv_name = 'X'
        elif instruction.name == 'Y': inv_name = 'Y'
        elif instruction.name == 'Z': inv_name = 'Z'
        elif instruction.name == 'SQRT_X': inv_name = 'SQRT_X_DAG'
        # ... others
        
        if inv_name:
            mini = stim.Circuit()
            mini.append(inv_name, instruction.targets_copy())
            
            # Force size to match
            if circuit.num_qubits > 0:
                # Add Identity on the last qubit (index num_qubits - 1)
                # Note: Stim infers size from max qubit index + 1.
                mini.append("I", [circuit.num_qubits - 1])
            
            inv_tableau = stim.Tableau.from_circuit(mini)
            
            if len(inv_tableau) != len(current_suffix):
                # This could happen if circuit uses higher indices than num_qubits?
                # Or num_qubits is larger than max index used in mini?
                # If inv_tableau is smaller, we can pad it.
                # But creating a new tableau is hard.
                # Let's just trust adding I on num_qubits-1 works.
                pass
            
            current_suffix = inv_tableau.then(current_suffix)
        
        if i % 100 == 0:
            print(f"Processed {i} gates...")

    print(f"Found {len(bad_faults)} bad faults.")
    for f in bad_faults[:10]:
        print(f)


if __name__ == "__main__":
    analyze()
