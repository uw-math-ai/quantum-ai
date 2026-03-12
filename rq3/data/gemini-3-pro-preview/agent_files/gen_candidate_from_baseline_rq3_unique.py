import stim
import sys

def main():
    try:
        circuit = stim.Circuit.from_file("baseline_rq3_unique.stim")
    except FileNotFoundError:
        print("Baseline file not found", file=sys.stderr)
        return

    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Get the tableau that creates the current state from |0>
    # current_inverse_tableau() gives T^-1 such that T^-1 * state = |0>
    # So we need its inverse to get T.
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize circuit
    # Use CZ gates (graph state)
    new_circuit = tableau.to_circuit(method="graph_state")
    
    # Replace RX with H to avoid resets (assuming input |0>)
    final_circuit = stim.Circuit()
    for instr in new_circuit:
        if instr.name == "RX":
            final_circuit.append("H", instr.targets_copy())
        elif instr.name == "TICK":
            pass # Remove ticks
        else:
            final_circuit.append(instr)

    # Print the raw circuit to stdout
    print(final_circuit)

if __name__ == "__main__":
    main()
