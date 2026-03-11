import stim
import sys

def main():
    # Load baseline
    try:
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        circuit = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    # Convert to tableau
    tableau = stim.Tableau.from_circuit(circuit)

    # Convert to graph state circuit
    # This automatically produces a circuit with H, S, CZ, and initialization
    # It might use RX (Reset X), which we need to convert to H if we assume |0> start.
    graph_circuit = tableau.to_circuit(method="graph_state")

    # Post-process to remove explicit resets
    # If the circuit starts with RX, it means it resets the qubit to X.
    # Since we assume start at |0>, RX is achieved by H.
    # If it starts with R (Reset Z), it means reset to |0>.
    # Since we assume start at |0>, R is Identity (can be removed).
    
    clean_circuit = stim.Circuit()
    for instruction in graph_circuit:
        if instruction.name == "RX":
            # RX target means "Reset to X". 
            # Equivalently: Reset Z (to 0) then H.
            # Since we are already at 0 (assumed), we just apply H.
            clean_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "R" or instruction.name == "RZ":
            # R target means "Reset to Z" (to 0).
            # Since we are already at 0, do nothing.
            pass
        elif instruction.name == "RY":
             # Should not happen in graph state usually, but Ry = Reset Y.
             # Reset 0 -> S -> H ? No.
             # Let's hope no RY.
             print(f"Warning: Unexpected reset gate {instruction.name}")
             clean_circuit.append(instruction)
        else:
            clean_circuit.append(instruction)

    # Output the cleaned circuit
    with open("candidate.stim", "w") as f:
        f.write(str(clean_circuit))

    print("Candidate generated in candidate.stim")

if __name__ == "__main__":
    main()
