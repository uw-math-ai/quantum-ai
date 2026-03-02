import stim
import re

def check_stabilizers(circuit: str, stabilizers: list[str]) -> dict[str, bool]:
    """Check if the given stabilizers are preserved by the circuit.

    Args:
        circuit: A string in the stim circuit format.
        stabilizers: A list of strings representing the stabilizers (e.g., ['XXII', 'ZIZI']).
            - Note that the stabilizers will be padded with 'I' to match the number of qubits in the circuit.
    Returns:
        A dictionary mapping each stabilizer to a boolean indicating if it is preserved.
    """
    circuit = preprocess_stim_text(circuit)
    circ = stim.Circuit(circuit)
    sim = stim.TableauSimulator()
    sim.do(circ)

    results = {}
    for stabilizer in stabilizers:
        pauli = stim.PauliString(stabilizer + 'I' * (circ.num_qubits - len(stabilizer)))
        expectation = sim.peek_observable_expectation(pauli)
        results[stabilizer] = expectation > 0
    return results

def preprocess_stim_text(raw: str) -> str:
    """
    Normalize a Stim circuit string so Stim can parse it reliably.
    - Converts literal '\\n' sequences into real newlines.
    - Strips leading/trailing whitespace per line.
    - Removes empty lines.
    - Collapses internal whitespace to single spaces.
    - (Optional) removes comment lines starting with '#'.
    """
    if raw is None:
        return ""

    text = raw.strip()

    # If the user wrote "\\n" inside a triple-quoted string, turn it into actual newlines.
    text = text.replace("\\n", "\n")

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        # collapse runs of whitespace to a single space
        line = re.sub(r"\s+", " ", line)
        lines.append(line)

    return "\n".join(lines) + ("\n" if lines else "")

if __name__ == "__main__":
    # Example: Check if a circuit prepares the |0000⟩ + |1111⟩ state (4-qubit GHZ)
    # This state is stabilized by: XXXX, ZIZI, IZZI, IIZZ

    # Circuit that should prepare this state
    circuit = """
     H 0 1\\nCX 0 1 0 4\\nH 2 3\\nCX 1 2 1 3 1 4 1 5 1 8 1 14 2 4 2 5 2 6 2 9 2 10 4 3 3 4 4 3 3 6 3 10 4 5 4 7 4 8 4 11 4 14 5 6 5 7 5 9 5 11 5 12 6 7 6 12 6 13 7 13 11 8 12 8 13 8 14 8 9 10 12 9 13 9 14 9 12 10 13 10 14 10 12 11 11 12 12 11 11 12 13 11 14 11 13 12 14 12 14 13
    """

    circuit = preprocess_stim_text(circuit)
    circuit_print = stim.Circuit(circuit)
    print(circuit_print.diagram())

    # Define your target stabilizers
    target_stabilizers = ["XXXXXXXXIIIIIII", "IXXIXXIIXXIXXII", "IIXXIXXIIXXXIXI", "IIIIXXXXIIIXXXX", "ZZZZIIIIIIIIIII", "IZZIZZIIIIIIIII", "IIZZIZZIIIIIIII", "IIIIZZZZIIIIIII", "IZIIZIIIZIIIZII", "IIZIIZIIIZIZIII", "IIZZIIIIIZZIIII", "IIIIZZIIIIIZZII", "IIIIIZZIIIIZIZI", "IIIIIIZZIIIIIZZ"]

    print(check_stabilizers(circuit, target_stabilizers))