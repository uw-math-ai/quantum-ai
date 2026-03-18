import stim
import sys

def generate_circuit():
    with open('baseline_job.stim', 'r') as f:
        baseline_circuit = stim.Circuit(f.read())
        
    sim = stim.TableauSimulator()
    sim.do(baseline_circuit)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize circuit using graph state method
    circuit = tableau.to_circuit(method='graph_state')
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == 'R':
            # R resets to |0>. If we assume input is |0>, this is a no-op.
            continue
        elif instruction.name == 'RX':
            # RX resets to |+>. If input is |0>, we can get |+> with H.
            new_circuit.append('H', instruction.targets_copy())
        elif instruction.name == 'RY':
            # RY resets to |i+>. If input is |0>, we can get |i+> with H then S.
            targets = instruction.targets_copy()
            new_circuit.append('H', targets)
            new_circuit.append('S', targets)
        else:
            new_circuit.append(instruction)

    with open('candidate_graph.stim', 'w') as f:
        print(new_circuit, file=f)

if __name__ == "__main__":
    generate_circuit()
