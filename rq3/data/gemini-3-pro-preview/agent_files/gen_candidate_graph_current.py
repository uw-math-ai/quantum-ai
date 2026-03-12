import stim
import sys

def main():
    stabilizers = []
    # Read from the current file I just created
    with open('target_stabilizers_current.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))

    # Try to create a Tableau from stabilizers
    # Use allow_redundant=True and allow_underconstrained=True just in case
    # to avoid errors if the set is not perfect.
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau from stabilizers: {e}")
        # If it fails, fallback to extracting tableau from baseline
        print("Falling back to baseline tableau extraction...")
        try:
            with open('baseline_current.stim', 'r') as f:
                baseline_text = f.read()
            baseline = stim.Circuit(baseline_text)
            sim = stim.TableauSimulator()
            sim.do(baseline)
            tableau = sim.current_inverse_tableau().inverse()
        except Exception as e2:
             print(f"Error extracting from baseline: {e2}")
             sys.exit(1)

    # Synthesize circuit using 'graph_state' method (optimizes for 0 CX, uses CZ)
    circuit = tableau.to_circuit(method="graph_state")
    
    # Post-processing: Replace RX with H (since we assume input |0>)
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        else:
            new_circuit.append(instruction)

    # print(new_circuit)
    with open('candidate.stim', 'w') as f:
        print(new_circuit, file=f)

if __name__ == "__main__":
    main()
