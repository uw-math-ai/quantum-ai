# Copied from Christian's code to test the new circuits 

import stim

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
    """Inject a Pauli fault on `qubit` AFTER gate at loc_index, then propagate through rest of circuit."""
    
    # Determine number of qubits
    all_qubits_set = set()
    for gate_name, targets in gate_list:
        all_qubits_set.update(targets)
    num_qubits = max(all_qubits_set) + 1 if all_qubits_set else 0
    
    # Create initial Pauli string (the fault we inject)
    initial_pauli = stim.PauliString(num_qubits)
    initial_pauli[qubit] = pauli
    
    # Build suffix circuit (from AFTER the fault location onward)
    suffix_circ = stim.Circuit()
    for i in range(loc_index + 1, len(gate_list)):
        gate_name, targets = gate_list[i]
        suffix_circ.append(gate_name, targets)
    
    # Propagate the Pauli through the suffix circuit
    if len(suffix_circ) == 0:
        final_pauli = initial_pauli
    else:
        tableau = stim.Tableau.from_circuit(suffix_circ, ignore_measurement=True)
        final_pauli = tableau(initial_pauli)
    
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

def error_weight_on(qubits, x_mask, z_mask=None, x_only=False):
    """Count how many qubits in `qubits` have errors.
    
    Args:
        qubits: List of qubit indices to check.
        x_mask: Set of qubits with X errors.
        z_mask: Set of qubits with Z errors (optional if x_only=True).
        x_only: If True, only count X errors (detectable by Z-basis measurement).
                If False, count any nontrivial Pauli (X, Y, or Z).
    """
    w = 0
    for q in qubits:
        if ((x_only and q in x_mask) or
            (not x_only and (q in x_mask or (z_mask is not None and q in z_mask)))):
                w += 1
    return w


def check_error_propagation(circuit: str, data_qubits: list[int], flag_qubits: list[int]):
    '''Check error propagation through the circuit for single-qubit Pauli faults.
    Args:
        circuit: A string in the stim circuit format.
        data_qubits: List of qubit indices considered as data qubits.
        flag_qubits: List of qubit indices considered as flag qubits.
    Returns: List of dictionaries containing error propagation results:
            - loc: Gate index after which the fault is injected.
            - gate: Gate name at that location.
            - fault_qubit: Qubit index where the fault is injected.
            - fault_pauli: Type of Pauli fault injected ('X', 'Y', 'Z').
            - final_paulis: Dictionary mapping qubit indices to their final Pauli after propagation.
            - data_weight: Number of data qubits affected by the fault (error propagation if > 1).
            - flag_weight: Number of flag qubits with an X error (error detected when >= 1).
    '''
    gate_list = parse_circuit_to_gate_list(stim.Circuit(circuit))
    
    results = []
    # Iterate through each gate in the gate list
    for gate_index, (gate_name, qubits) in enumerate(gate_list):
        for q in qubits:
            # Only inject faults on data qubits
            if q not in data_qubits:
                continue
            
            for pauli in ("X", "Z", "Y"):
                final_paulis, x_mask, z_mask = propagate_fault(gate_list, gate_index, pauli, q)
                data_w = error_weight_on(data_qubits, x_mask, z_mask)
                flag_w = error_weight_on(flag_qubits, x_mask, x_only=True)

                results.append({
                    "loc": gate_index,
                    "gate": gate_name,
                    "fault_qubit": q,
                    "fault_pauli": pauli,
                    "final_paulis": final_paulis,
                    "data_weight": data_w,
                    "flag_weight": flag_w,
                })
    return results

def check_fault_tolerance(circuit: str, data_qubits: list[int], flag_qubits: list[int]) -> tuple[list, bool]:
    '''Check if the circuit is fault-tolerant against single-qubit Pauli faults.
    A circuit is fault-tolerant if:
        - Every single-qubit Pauli fault causes at most one data qubit error without flagging.
        - Every single-qubit Pauli fault that causes more than one data qubit error causes at least one flag qubit to have an X error.
    '''
    results = check_error_propagation(circuit, data_qubits, flag_qubits)
    for r in results:
        if r["data_weight"] > 1 and r["flag_weight"] < 1:
            return results, False
    return results, True

if __name__ == "__main__":
    # data_qubits = list(range(8))
    # flag_qubits = list(range(8, 16))

    data_qubits = list(range(3))
    flag_qubits = list(range(3, 5))

    # data_qubits = list(range(2))
    # flag_qubits = list(range(2, 3))
    all_qubits = data_qubits + flag_qubits

    # Stim circuit

    # from fault_tolerant_circuits.py: circuit_1
    # circuit = """
    #     H 0
    #     CX 0 4
    #     CX 0 2
    #     CX 0 1
    #     CX 2 3 
    #     CX 4 6 
    #     CX 4 5
    #     CX 6 7
    #     H 8
    #     CX 8 14
    #     CX 8 10
    #     CX 8 9
    #     CX 10 11 
    #     CX 12 14 
    #     CX 12 13
    #     CX 14 15
    #     CX 1 9
    #     CX 7 8
    #     M 9
    #     CX 2 10
    #     CX 3 11
    #     CX 4 12
    #     CX 5 13
    #     CX 0 15
    #     CX 6 14
    #     M 15
    #     M 8
    #     M 10
    #     M 11
    #     M 12
    #     M 13
    #     M 14
    #     """

    # from fault_tolerant_circuits.py: circuit_2
    circuit = """
        H 0 
        CX 0 3
        CX 0 1
        CX 0 2
        CX 0 4
        M 3
        M 4
        """

    # circuit = """
    #     H 0 1
    #     CX 0 2 1 2
    #     M 2
    #     H 0 1
    #     CX 0 2 1 2
    #     M 2
    #     H 0 1
    #     """

    results = check_error_propagation(circuit, data_qubits, flag_qubits)

    print("loc | gate   | fault  | data_w | flag_w | final_paulis (truncated)")
    for r in results:
        pauli_str = ''.join(r['final_paulis'][q] for q in sorted(r['final_paulis']))[:80]
        print(f"{r['loc']:3d} | {r['gate']:<6s} | {r['fault_pauli']}{r['fault_qubit']:>3d} | "
            f"{r['data_weight']:6d} | {r['flag_weight']:6d} | {pauli_str}")
