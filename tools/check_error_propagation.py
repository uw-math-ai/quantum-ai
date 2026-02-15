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
        if num_qubits > 0:
            # Ensure the tableau width matches the full circuit width.
            suffix_circ.append("I", [num_qubits - 1])
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

def ft_score(circuit: str, data_qubits: list[int], flag_qubits: list[int], d: int = 1, p: float = 1.0) -> float:
    '''Compute the fault-tolerance score based on weighted undetected faults.

    FT = 1 - sum(weight(f)^p for undetected faults with weight(f) > floor((d-1)/2))
             / sum(weight(f)^p for faults with weight(f) > floor((d-1)/2))
    where weight(f) is the number of data-qubit errors and undetected means no X on any flag qubit.
    '''
    results = check_error_propagation(circuit, data_qubits, flag_qubits)
    threshold = (d - 1) // 2
    numerator = 0.0
    denominator = 0.0
    for r in results:
        weight = r["data_weight"]
        if weight > threshold:
            weighted = float(weight ** p)
            denominator += weighted
            if r["flag_weight"] == 0:
                numerator += weighted
    if denominator == 0.0:
        return 1.0
    return 1.0 - (numerator / denominator)

if __name__ == "__main__":
    data_qubits = [0, 1, 2, 3]
    flag_qubits = []
    all_qubits = data_qubits + flag_qubits

    # Stim circuit
    circuit = """
        CX 0 1
        CX 1 2
        CX 2 3
    """

    results = check_error_propagation(circuit, data_qubits, flag_qubits)

    print("loc | gate   | fault  | data_w | flag_w | final_paulis (truncated)")
    for r in results:
        pauli_str = ''.join(r['final_paulis'][q] for q in sorted(r['final_paulis']))[:80]
        print(f"{r['loc']:3d} | {r['gate']:<6s} | {r['fault_pauli']}{r['fault_qubit']:>3d} | "
            f"{r['data_weight']:6d} | {r['flag_weight']:6d} | {pauli_str}")