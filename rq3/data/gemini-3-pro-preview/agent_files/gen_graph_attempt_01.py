import stim
import sys

def main():
    try:
        with open("baseline_attempt_01.stim", "r") as f:
            baseline_text = f.read()
            baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    print(f"Loaded baseline with {baseline.num_qubits} qubits.")

    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    
    try:
        circuit_graph = tableau.to_circuit(method="graph_state")
        
        processed_lines = []
        for instruction in circuit_graph:
            if instruction.name == "R":
                continue
            elif instruction.name == "RX":
                # Replace RX with H for |0> input
                targets = instruction.targets_copy()
                processed_lines.append(stim.CircuitInstruction("H", targets))
            else:
                processed_lines.append(instruction)
        
        final_circuit = stim.Circuit()
        for instr in processed_lines:
            final_circuit.append(instr)
            
        with open("candidate_attempt_01.stim", "w") as f:
            f.write(str(final_circuit))
            
        print(f"Generated candidate_attempt_01.stim")
        print(f"Baseline instructions: {len(baseline)}")
        print(f"Candidate instructions: {len(final_circuit)}")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    main()
