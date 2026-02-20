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
     H 0 16
CX 0 16
H 0 16
CX 0 16
H 0 16
CX 0 16
H 0 16
CX 0 15
H 7
CX 7 0 5 1 1 5 5 1
H 1 2 3 4 6 16
CX 1 2 1 3 1 4 1 6 1 7 1 13 1 15 1 16 7 2 2 7 7 2 2 7 2 11 3 2 7 3 3 7 7 3 3 10 3 15 4 6 4 7 4 11 4 12 4 13 4 15 4 16 16 5 5 16 16 5
H 16
CX 5 6 5 8 5 12 5 16 7 6 6 7 7 6 6 12 6 15 10 7 7 10 10 7 7 12 11 7 16 8 8 16 16 8 8 9 8 12 8 14 10 8 10 9 9 10 10 9 9 10 9 12 9 16 10 12 10 13 12 10 13 10 14 10 15 10 14 11 11 14 14 11 11 12 11 16 13 11 16 12 12 16 16 12 13 12 16 13 13 16 16 13 15 13 15 14 14 15 15 14 14 15 16 15 15 16 16 15
    """

    circuit_print = stim.Circuit(circuit)
    print(circuit_print.diagram())

    # Define your target stabilizers
    target_stabilizers = [
      "IIIIIXIIIXIXXIIII",
            "IIIIIIIIXIXIIXIXI",
            "IIIXIIIXIIIIIIXIX",
            "IIXIIIXIIIIIIIXIX",
            "IIIIXXXXXIXXIIIIX",
            "IXIIXIIIIIXIIXIII",
            "IIIIIIIIXXIXIIIXI",
            "XIXXIIIIIIIIIIXII",
            "IIIIIZIIIZIZZIIII",
            "IIIIIIIIZIZIIZIZI",
            "IIIZIIIZIIIIIIZIZ",
            "IIZIIIZIIIIIIIZIZ",
            "IIIIZZZZZIZZIIIIZ",
            "IZIIZIIIIIZIIZIII",
            "IIIIIIIIZZIZIIIZI",
            "ZIZZIIIIIIIIIIZII"
    ]

    print(check_stabilizers(circuit, target_stabilizers))