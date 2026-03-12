import stim
import sys

def generate_from_baseline(baseline_file, output_file):
    try:
        with open(baseline_file, 'r') as f:
            baseline_text = f.read()
        
        circuit = stim.Circuit(baseline_text)
        num_qubits = circuit.num_qubits
        
        # Simulate to get tableau
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Extract tableau
        # current_inverse_tableau().inverse() gives the state P such that P|0> = output.
        tableau = sim.current_inverse_tableau().inverse()
        
        # Synthesize using graph_state
        new_circuit = tableau.to_circuit(method="graph_state")
        
        # Filter out operations on qubits beyond the baseline range, if any (just in case)
        # and replace RX, RY with H, S equivalents to avoid resets and ensure compatibility.
        
        final_circuit = stim.Circuit()
        for instr in new_circuit:
            name = instr.name
            targets = instr.targets_copy()
            
            # Filter targets > num_qubits if needed?
            # Actually, if the tableau has non-identity Pauli on qubit 100, we must keep it or we change the state.
            # But baseline only has 60 qubits.
            # We assume the simulator didn't add garbage on higher qubits.
            
            # Replacements
            if name == "RX":
                 # RX -> H (assuming |0> input)
                 final_circuit.append("H", targets)
            elif name == "RY":
                 # RY -> H S
                 final_circuit.append("H", targets)
                 final_circuit.append("S", targets)
            elif name == "RZ":
                 # RZ -> I (drop)
                 pass
            elif name == "X":
                 # Keep X, or decompose to H S S H? X is better (volume=1)
                 final_circuit.append("X", targets)
            elif name == "Y":
                 final_circuit.append("Y", targets)
            elif name == "Z":
                 final_circuit.append("Z", targets)
            else:
                final_circuit.append(instr)
                
        with open(output_file, 'w') as f:
            print(final_circuit, file=f)
            
        print(f"Generated {output_file} with {len(final_circuit)} instructions.")
        
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    generate_from_baseline("baseline.stim", "candidate_graph_baseline.stim")
