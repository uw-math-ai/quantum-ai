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
       CX 2 0 0 2 2 0
       H 0 4
       CX 0 3 0 4
       H 2
       CX 2 0 3 1 1 3 3 1
       H 1 2 4
       CX 1 2 1 4
       H 3
       CX 3 1
       H 3
       CX 2 3
       H 4
       CX 4 2 4 3 3 4 4 3
       H 3
       CX 3 4
       H 4
       CX 4 3
       H 2
       S 2 2
       H 2
       S 0 0 2 2
     """

    circuit_print = stim.Circuit(circuit)
    print(circuit_print.diagram())

    # Define your target stabilizers
    target_stabilizers = [
      "XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"
    ]

    print(check_stabilizers(circuit, target_stabilizers))