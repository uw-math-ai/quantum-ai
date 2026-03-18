import stim
import sys

def solve():
    print("Reading stabilizers...")
    try:
        with open("target_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print("target_stabilizers.txt not found.")
        return

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        if ". " in line:
            line = line.split(". ", 1)[1]
        if not line: 
            continue
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Skipping invalid line: {line} ({e})")

    if not stabilizers:
        print("No stabilizers found.")
        return

    num_qubits = len(stabilizers[0])
    print(f"Found {len(stabilizers)} stabilizers for {num_qubits} qubits.")

    # Create tableau
    try:
        # allow_redundant=True: The list might not be minimal.
        # allow_underconstrained=True: The list might not define a unique state.
        # We want ANY state that satisfies these stabilizers.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error building tableau: {e}")
        return

    # Synthesize using graph state method
    # This produces a circuit with H, S, CZ, and Pauli gates.
    # It tends to minimize CX (by using CZ instead, which often counts as 0 CX or low volume).
    print("Synthesizing graph state circuit...")
    try:
        circuit = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error synthesizing circuit: {e}")
        return

    # Post-process to make it compatible with |0> input
    # Replace RX (reset X) with H.
    # Replace R (reset Z) with I (if we assume |0> input).
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "R" or instruction.name == "RZ":
            # Redundant on |0> input
            pass
        elif instruction.name == "MY" or instruction.name == "MX" or instruction.name == "MZ":
             # If graph state adds measurements, we might need them? 
             # Usually it doesn't unless we asked for a measurement-based thing.
             # We'll keep them but warn.
             print(f"Warning: Measurement {instruction.name} found.")
             new_circuit.append(instruction)
        elif instruction.name == "TICK":
             pass
        else:
            new_circuit.append(instruction)

    # Output candidate
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))
    
    print("Candidate written to candidate.stim")

if __name__ == "__main__":
    solve()
