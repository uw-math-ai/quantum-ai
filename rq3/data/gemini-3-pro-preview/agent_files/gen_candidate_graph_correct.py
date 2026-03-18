import stim
import sys

def main():
    # Read baseline circuit
    try:
        baseline = stim.Circuit.from_file("baseline_correct_final.stim")
    except Exception as e:
        print(f"Error reading baseline: {e}")
        return

    # Get the Tableau of the state prepared by the baseline
    sim = stim.TableauSimulator()
    sim.do(baseline)
    # The current inverse tableau maps the current state to the initial state |0>.
    # Its inverse is the forward tableau, which represents the current state (U applied to |0>).
    state_tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize optimized circuit using graph state method
    # This produces a circuit with H, S, CZ, and Pauli gates (no CX)
    candidate = state_tableau.to_circuit(method="graph_state")
    
    # Post-process to replace RX with H for |0> input
    final_circuit = stim.Circuit()
    for instruction in candidate:
        if instruction.name == "RX":
            # RX target resets target to |+>. H |0> -> |+>.
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 20):
                 final_circuit.append("H", targets[i:i+20])
                 final_circuit.append("TICK")
        elif instruction.name == "RY":
             # RY resets to |+i>. S * H * |0> = |+i>.
             targets = instruction.targets_copy()
             for i in range(0, len(targets), 20):
                 final_circuit.append("H", targets[i:i+20])
                 final_circuit.append("S", targets[i:i+20])
                 final_circuit.append("TICK")
        elif instruction.name == "RZ" or instruction.name == "R":
             pass
        elif instruction.name == "TICK":
            pass
        elif instruction.name == "CZ":
            # Split CZ into chunks of 10 pairs (20 targets)
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 20):
                final_circuit.append("CZ", targets[i:i+20])
                final_circuit.append("TICK")
        elif instruction.name in ["H", "X", "Y", "Z", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"]:
             # Split single qubit gates into smaller chunks
             targets = instruction.targets_copy()
             for i in range(0, len(targets), 20):
                 final_circuit.append(instruction.name, targets[i:i+20])
                 final_circuit.append("TICK")
        else:
            final_circuit.append(instruction)
            
    # Output to file
    with open("candidate_graph_correct.stim", "w") as f:
        f.write(str(final_circuit))
        
    print("Generated candidate_graph_correct.stim")

if __name__ == "__main__":
    main()
