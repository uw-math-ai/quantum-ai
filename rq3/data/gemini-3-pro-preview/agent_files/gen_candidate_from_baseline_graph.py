import stim

def main():
    # Read baseline circuit
    try:
        baseline = stim.Circuit.from_file("baseline_new.stim")
    except Exception as e:
        print(f"Error reading baseline: {e}")
        return

    # Get the Tableau of the state prepared by the baseline
    # We simulate the circuit on |0> state.
    sim = stim.TableauSimulator()
    sim.do(baseline)
    # The current inverse tableau maps the current state to the initial state |0>.
    # Its inverse is the forward tableau, which represents the current state (U applied to |0>).
    # Actually, stim's Tableau represents the stabilizers of the state if we consider the generators.
    # U * Z_i * U_dagger are the stabilizers.
    # sim.current_inverse_tableau().inverse() gives the tableau of U.
    # The stabilizers of U|0> are the Z-outputs of this tableau.
    # But wait, to_circuit("graph_state") takes a Tableau.
    # If the Tableau represents U, does to_circuit produce U?
    # No, "graph_state" method produces a state preparation circuit.
    # It assumes the input tableau represents a stabilizer STATE (or a tableau whose Z outputs are the stabilizers).
    # Yes, passing the forward tableau of U (which maps Z_i to S_i) works.
    
    state_tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize optimized circuit
    # method="graph_state" produces 0-CX circuits (using CZ).
    candidate = state_tableau.to_circuit(method="graph_state")
    
    # Post-process to replace RX with H for |0> input
    # RX resets to |+>. H on |0> goes to |+>.
    final_circuit = stim.Circuit()
    for instruction in candidate:
        if instruction.name == "RX":
            targets = instruction.targets_copy()
            final_circuit.append("H", targets)
        elif instruction.name == "RY":
             # RY resets to |+i>. S * H * |0> = |+i>.
             targets = instruction.targets_copy()
             final_circuit.append("H", targets)
             final_circuit.append("S", targets)
        elif instruction.name == "RZ" or instruction.name == "R":
             # Reset to |0>. Do nothing if input is |0>.
             pass
        elif instruction.name == "TICK":
            # Remove ticks for final submission to be clean
            pass
        else:
            final_circuit.append(instruction)
            
    # Output
    with open("candidate_graph_baseline.stim", "w") as f:
        f.write(str(final_circuit))
        
    print("Generated candidate_graph_baseline.stim")
    print(f"Original instructions: {len(baseline)}")
    print(f"New instructions: {len(final_circuit)}")

if __name__ == "__main__":
    main()
