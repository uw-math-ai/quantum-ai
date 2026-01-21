import stim

# --- Steane code definitions ---
X_stabilizers = [
    [0, 1, 2, 3],
    [0, 1, 4, 5],
    [0, 2, 4, 6],
]

Z_stabilizers = [
    [0, 1, 2, 3],
    [0, 1, 4, 5],
    [0, 2, 4, 6],
]

# Syndrome → qubit index for single-qubit error correction
syndrome_lookup = {
    (1,1,1): 0,
    (1,1,0): 1,
    (1,0,1): 2,
    (1,0,0): 3,
    (0,1,1): 4,
    (0,1,0): 5,
    (0,0,1): 6,
}

# Logical operators for Steane code
logical_X = [0,1,2,3,4,5,6]
logical_Z = [0,1,2,3,4,5,6]

# --- Helper functions ---
def measure_syndrome(sim, stabilizers):
    """Return the syndrome as a tuple for a simulator."""
    synd = []
    for s in stabilizers:
        val = 0
        for q in s:
            val ^= sim.measure(q)
        synd.append(val)
    return tuple(synd)

def ideal_steane_decoder(sim):
    """Correct any single-qubit X or Z errors."""
    # Correct Z errors using X stabilizers
    X_synd = measure_syndrome(sim, X_stabilizers)
    if X_synd != (0,0,0):
        sim.x(syndrome_lookup[X_synd])
    # Correct X errors using Z stabilizers
    Z_synd = measure_syndrome(sim, Z_stabilizers)
    if Z_synd != (0,0,0):
        sim.z(syndrome_lookup[Z_synd])

def fault_tolerant_decode(sim, basis='Z'):
    """
    Apply ideal Steane decoder in the given logical basis.
    basis: 'Z' for |0_L>/|1_L>, 'X' for |+_L>/|-_L>
    """
    if basis == 'X':
        # Rotate to Z basis
        for q in range(7):
            sim.h(q)
    ideal_steane_decoder(sim)
    if basis == 'X':
        # Rotate back if needed
        for q in range(7):
            sim.h(q)

def check_logical_state(sim, target_state='0'):
    """Check logical state using measure_observable."""
    Z_val = sim.measure_observable(stim.PauliString("ZZZZZZZ"))
    X_val = sim.measure_observable(stim.PauliString("XXXXXXX"))

    if target_state == '0':
        return Z_val == 0
    elif target_state == '1':
        return Z_val == 1
    elif target_state == '+':
        return X_val == 0
    elif target_state == '-':
        return X_val == 1
    else:
        raise ValueError(f"Unknown target_state {target_state}")

# --- Main fault-tolerance checker ---
def steane_fault_propagation(circuit_str, target_state='0'):
    """
    Inject single-qubit Pauli faults and check the fraction that propagate
    for a given single-qubit logical state.
    """
    circuit = stim.Circuit(circuit_str)

    total_faults = 0
    propagating_faults = 0

    # Determine decoding basis
    basis = 'Z' if target_state in ['0','1'] else 'X'

    for idx, instr in enumerate(circuit):
        qubits = instr.targets_copy()
        if not qubits:
            continue  # skip classical/empty instructions
        total_faults += 1

        fault_propagates = False
        for q in qubits:
            for pauli in ['X','Y','Z']:
                sim = stim.TableauSimulator()
                # Run circuit up to and including the fault
                for i, g in enumerate(circuit):
                    sim.do(g)
                    if i == idx:
                        getattr(sim, pauli.lower())(q)
                        break
                # Run remainder of circuit
                for j in range(idx + 1, len(circuit)):
                    sim.do(circuit[j])
                # Apply fault-tolerant decoding in correct basis
                fault_tolerant_decode(sim, basis)
                # Check if logical state changed
                if not check_logical_state(sim, target_state):
                    fault_propagates = True
                    break
            if fault_propagates:
                break

        if fault_propagates:
            propagating_faults += 1

    if total_faults == 0:
        return 0.0
    return propagating_faults / total_faults


def _pauli_string_for_qubits(*, qubits, pauli: str) -> stim.PauliString:
    if pauli not in {"X", "Y", "Z"}:
        raise ValueError(pauli)
    qs = [int(q) for q in qubits]
    if not qs:
        return stim.PauliString("")
    n = max(qs) + 1
    chars = ["_"] * n
    for q in qs:
        chars[q] = pauli
    return stim.PauliString("".join(chars))


def _peek_stabilizer_bit(sim: stim.TableauSimulator, p: stim.PauliString) -> int:
    """Return 0 for +1 eigenvalue, 1 for -1 eigenvalue.

    Uses peek when deterministic; otherwise measures the Pauli observable.
    """
    e = sim.peek_observable_expectation(p)
    if e == +1:
        return 0
    if e == -1:
        return 1
    if e == 0:
        # Not deterministic in this branch; measure the stabilizer.
        return int(sim.measure_observable(p))
    raise RuntimeError(f"Unexpected expectation {e} for {p}")


def peek_syndrome(sim: stim.TableauSimulator, stabilizers, *, pauli: str, offset: int = 0):
    """Non-demolition syndrome: returns tuple of bits (0=+1, 1=-1)."""
    synd = []
    for s in stabilizers:
        p = _pauli_string_for_qubits(qubits=[offset + q for q in s], pauli=pauli)
        synd.append(_peek_stabilizer_bit(sim, p))
    return tuple(synd)


def ideal_steane_decoder_peek(sim: stim.TableauSimulator, *, offset: int = 0) -> None:
    """Correct any single-qubit X/Z error on a 7-qubit Steane block (non-demolition)."""
    # X-type stabilizers detect Z errors.
    x_synd = peek_syndrome(sim, X_stabilizers, pauli="X", offset=offset)
    if x_synd != (0, 0, 0):
        sim.z(offset + syndrome_lookup[x_synd])

    # Z-type stabilizers detect X errors.
    z_synd = peek_syndrome(sim, Z_stabilizers, pauli="Z", offset=offset)
    if z_synd != (0, 0, 0):
        sim.x(offset + syndrome_lookup[z_synd])


def fault_tolerant_decode_peek(sim: stim.TableauSimulator, *, offset: int = 0) -> None:
    """Convenience wrapper for peek-based decoding of one Steane block."""
    ideal_steane_decoder_peek(sim, offset=offset)


def check_bell_state(
    sim: stim.TableauSimulator,
    target_state: str,
    *,
    offset_a: int = 0,
    offset_b: int = 14,
) -> bool:
    """
    Check a logical Bell state via logical stabilizers:
      |Phi±> : ZZ = +1, XX = ±1
      |Psi±> : ZZ = -1, XX = ±1
    Returns True when (ZZ, XX) match the target.
    """
    target_state = target_state.lower().replace("_l", "").replace(" ", "")

    z_qubits = [offset_a + i for i in range(7)] + [offset_b + i for i in range(7)]
    x_qubits = [offset_a + i for i in range(7)] + [offset_b + i for i in range(7)]

    zz_bit = _peek_stabilizer_bit(sim, _pauli_string_for_qubits(qubits=z_qubits, pauli="Z"))
    xx_bit = _peek_stabilizer_bit(sim, _pauli_string_for_qubits(qubits=x_qubits, pauli="X"))

    if target_state in {"phi+", "phiplus", "φ+"}:
        return zz_bit == 0 and xx_bit == 0
    if target_state in {"phi-", "phiminus", "φ-"}:
        return zz_bit == 0 and xx_bit == 1
    if target_state in {"psi+", "psiplus", "ψ+"}:
        return zz_bit == 1 and xx_bit == 0
    if target_state in {"psi-", "psiminus", "ψ-"}:
        return zz_bit == 1 and xx_bit == 1
    raise ValueError(f"Unknown Bell target_state {target_state}")


# --- Example usage ---
if __name__ == "__main__":
    # Target logical state |0_L>
    target_circuit = """
    H 7
    CX 7 8
    CX 8 9
    CX 9 10

    CX 7 11
    CX 8 11
    M 11
    R 11

    CX 7 0
    CX 8 1
    CX 9 2
    CX 10 3

    H 7 8 9 10
    M 7 8 9 10
    R 7 8 9 10


    H 7
    CX 7 8
    CX 8 9
    CX 9 10

    CX 7 11
    CX 8 11
    M 11
    R 11

    CX 7 0
    CX 8 1
    CX 9 4
    CX 10 5

    H 7 8 9 10
    M 7 8 9 10
    R 7 8 9 10


    H 7
    CX 7 8
    CX 8 9
    CX 9 10

    CX 7 11
    CX 8 11
    M 11
    R 11

    CX 7 0
    CX 8 2
    CX 9 4
    CX 10 6

    H 7 8 9 10
    M 7 8 9 10
    R 7 8 9 10

    H 0 1 2 3 4 5 6
    """

    test_circuit = target_circuit

    # fraction_0 = steane_fault_propagation(test_circuit, target_state='1')
    # print(f"Fault propagation fraction for |1_L>: {fraction_0:.4f}")

    fraction_plus = steane_fault_propagation(test_circuit, target_state='+')
    print(f"Fault propagation fraction for |+_L>: {fraction_plus:.4f}")