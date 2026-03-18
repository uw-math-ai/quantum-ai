import stim
import sys

def main():
    try:
        with open("my_baseline.stim", "r") as f:
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
        
        # Post-process to optimize for our specific instruction set and initial state |0>
        # graph_state output usually has R, RX, CZ, H, S...
        
        processed_lines = []
        for instruction in circuit_graph:
            if instruction.name == "R":
                # We assume we start in |0>, so Reset is redundant if it's at the beginning.
                # But to be safe, we can just remove it if we know the input is |0>.
                # However, if the circuit uses ancillary qubits, they might need reset?
                # The baseline uses 49 qubits. The task usually implies starting state is |0> on all.
                continue
            elif instruction.name == "RX":
                # RX on |0> creates |+>. H on |0> creates |+>.
                # RX is often not in the standard gate set or has higher cost. H is better.
                # Check targets.
                targets = instruction.targets_copy()
                processed_lines.append(stim.CircuitInstruction("H", targets))
            else:
                processed_lines.append(instruction)
        
        final_circuit = stim.Circuit()
        for instr in processed_lines:
            final_circuit.append(instr)
            
        with open("candidate_graph_v2.stim", "w") as f:
            f.write(str(final_circuit))
            
        print(f"Generated candidate_graph_v2.stim")
        print(f"Baseline instructions: {len(baseline)}")
        print(f"Candidate instructions: {len(final_circuit)}")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    main()
