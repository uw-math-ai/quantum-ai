import stim

def check_stabilizers(circuit: str, stabilizers: list[str]) -> dict[str, bool]:
    """Check if the given stabilizers are preserved by the circuit.

    Args:
        circuit: A string in the stim circuit format.
        stabilizers: A list of strings representing the stabilizers (e.g., ['XXII', 'ZIZI']).
            - Note that the stabilizers will be padded with 'I' to match the number of qubits in the circuit.
    Returns:
        A dictionary mapping each stabilizer to a boolean indicating if it is preserved.
    """
    circ = stim.Circuit(circuit)
    sim = stim.TableauSimulator()
    sim.do(circ)

    results = {}
    for stabilizer in stabilizers:
        pauli = stim.PauliString(stabilizer + 'I' * (circ.num_qubits - len(stabilizer)))
        expectation = sim.peek_observable_expectation(pauli)
        results[stabilizer] = expectation > 0
    return results

if __name__ == "__main__":
    # Example: Check if a circuit prepares the |0000⟩ + |1111⟩ state (4-qubit GHZ)
    # This state is stabilized by: XXXX, ZIZI, IZZI, IIZZ

    # Circuit that should prepare this state
    circuit = """
        H 0
        CX 0 1
        CX 1 2
        CX 2 3
    """

    # Define your target stabilizers
    target_stabilizers = [
        "XXXX",
        "XIXI",
        "IZZI",
        "IIZZ",
    ]

    print(check_stabilizers(circuit, target_stabilizers))