import stim

# -----------------------------
# USER PARAMETERS
# -----------------------------
data_qubits = [0, 1, 2]
flag_qubits = []
all_qubits = data_qubits + flag_qubits

# Stim circuit
circuit = stim.Circuit("""
    CZ 0 1
    CZ 1 2
    CZ 2 3
""")

def parse_circuit_to_gate_list(circuit):
    """Parse a Stim circuit into individual gates for fault injection."""
    gate_list = []
    for instruction in circuit:
        if instruction.name in ['CX', 'CY', 'CZ', 'CNOT']:
            # Two-qubit gates: split into individual pairs
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                qubit_a = targets[i].value
                qubit_b = targets[i+1].value
                gate_list.append((instruction.name, [qubit_a, qubit_b]))
        elif instruction.name in ['M', 'MX', 'MY', 'MZ', 'MR', 'MRX', 'MRY', 'MRZ']:
            # Measurement: one entry per qubit
            for tg in instruction.targets_copy():
                if hasattr(tg, 'value'):
                    gate_list.append((instruction.name, [tg.value]))
        elif instruction.name in ['H', 'X', 'Y', 'Z', 'S', 'S_DAG', 'SQRT_X', 'SQRT_Y']:
            # Single qubit gates
            for tg in instruction.targets_copy():
                if hasattr(tg, 'value'):
                    gate_list.append((instruction.name, [tg.value]))
        else:
            # General case: extract all qubit targets
            qubits = []
            for tg in instruction.targets_copy():
                if hasattr(tg, 'value'):
                    qubits.append(tg.value)
            if qubits:
                gate_list.append((instruction.name, qubits))
    return gate_list

gate_list = parse_circuit_to_gate_list(circuit)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def inject_pauli(sim, pauli, qubit):
    """Inject X, Z, or Y fault on a qubit."""
    if pauli == "X":
        sim.x(qubit)
    elif pauli == "Z":
        sim.z(qubit)
    elif pauli == "Y":
        sim.x(qubit)
        sim.z(qubit)
    else:
        raise ValueError(pauli)

def propagate_fault(gate_list, loc_index, pauli, qubit):
    """Simulate up to loc_index, inject a Pauli on `qubit`, then run the rest."""
    
    # Build suffix circuit (from fault location onward)
    suffix_circ = stim.Circuit()
    for i in range(loc_index, len(gate_list)):
        gate_name, targets = gate_list[i]
        suffix_circ.append(gate_name, targets)
    
    # Determine number of qubits
    all_qubits_set = set()
    for gate_name, targets in gate_list:
        all_qubits_set.update(targets)
    num_qubits = max(all_qubits_set) + 1 if all_qubits_set else 0
    
    # Create initial Pauli string (the fault we inject)
    initial_pauli = stim.PauliString(num_qubits)
    initial_pauli[qubit] = pauli
    
    # Get the tableau for the suffix circuit
    tableau = stim.Tableau.from_circuit(suffix_circ, ignore_measurement=True)
    
    # Transform the Pauli through the circuit
    # We need to manually apply the tableau transformation
    final_pauli_x = stim.PauliString(num_qubits)
    final_pauli_z = stim.PauliString(num_qubits)
    
    # For each qubit in the initial Pauli, look up how it transforms
    for q in range(num_qubits):
        p = initial_pauli[q]
        if p == 1:  # X on qubit q
            # X_q transforms according to tableau's X output for qubit q
            final_pauli_x *= tableau.x_output(q)
        elif p == 3:  # Z on qubit q  
            # Z_q transforms according to tableau's Z output for qubit q
            final_pauli_z *= tableau.z_output(q)
        elif p == 2:  # Y on qubit q (which is X*Z)
            # Y = iXZ, so it transforms as X_q * Z_q
            final_pauli_x *= tableau.x_output(q)
            final_pauli_z *= tableau.z_output(q)
    
    # Combine X and Z parts (ignoring phase)
    final_pauli = final_pauli_x * final_pauli_z
    
    # Extract X and Z masks from final Pauli string
    x_mask = set()
    z_mask = set()
    final_paulis = {}
    
    for q in range(num_qubits):
        p = final_pauli[q]
        if p == 1:  # X
            x_mask.add(q)
            final_paulis[q] = 'X'
        elif p == 2:  # Y
            x_mask.add(q)
            z_mask.add(q)
            final_paulis[q] = 'Y'
        elif p == 3:  # Z
            z_mask.add(q)
            final_paulis[q] = 'Z'
        else:  # I
            final_paulis[q] = 'I'
    
    return final_paulis, x_mask, z_mask

def error_weight_on(qubits, x_mask, z_mask):
    """Count how many qubits in `qubits` have a nontrivial Pauli (I !=)."""
    w = 0
    for q in qubits:
        if (q in x_mask) or (q in z_mask):
            w += 1
    return w

# -----------------------------
# RUN FAULT PROPAGATION TABLE
# -----------------------------
results = []

# Iterate through each gate in the gate list
for gate_index, (gate_name, qubits) in enumerate(gate_list):
    for q in qubits:
        for pauli in ("X", "Z", "Y"):
            final_paulis, x_mask, z_mask = propagate_fault(gate_list, gate_index, pauli, q)
            data_w = error_weight_on(data_qubits, x_mask, z_mask)
            flag_w = error_weight_on(flag_qubits, x_mask, z_mask)

            results.append({
                "loc": gate_index,
                "gate": gate_name,
                "fault_qubit": q,
                "fault_pauli": pauli,
                "final_paulis": final_paulis,
                "data_weight": data_w,
                "flag_weight": flag_w,
            })

# -----------------------------
# PRINT SUMMARY
# -----------------------------
print("loc | gate   | fault  | data_w | flag_w | final_paulis (truncated)")
for r in results:
    pauli_str = ''.join(r['final_paulis'][q] for q in sorted(r['final_paulis']))[:80]
    heavy = "YES" if r['data_weight'] > 1 else "no"
    print(f"{r['loc']:3d} | {r['gate']:<6s} | {r['fault_pauli']}{r['fault_qubit']:>3d} | "
          f"{r['data_weight']:6d} | {r['flag_weight']:6d} | {pauli_str} (heavy? {heavy})")
