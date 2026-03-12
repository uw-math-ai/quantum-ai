import stim
import sys

def generate():
    # Load baseline
    print('Loading baseline...')
    with open('baseline.stim', 'r') as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    print(f'Baseline qubits: {baseline.num_qubits}')

    # Get Tableau
    print('Simulating baseline...')
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()

    # Synthesize elimination
    print('Synthesizing elimination...')
    candidate_elim = tableau.to_circuit(method='elimination')
    with open('candidate_elimination.stim', 'w') as f:
        f.write(str(candidate_elim))

    # Synthesize graph state
    print('Synthesizing graph state...')
    candidate = tableau.to_circuit(method='graph_state')
    
    new_circuit = stim.Circuit()
    for instruction in candidate:
        if instruction.name == 'RX':
            targets = instruction.targets_copy()
            new_circuit.append('H', targets)
        elif instruction.name == 'R':
            pass
        elif instruction.name == 'RZ':
            pass
        elif instruction.name == 'RY':
             pass
        else:
            new_circuit.append(instruction)

    # Save candidate
    print('Saving candidate.stim...')
    with open('candidate.stim', 'w') as f:
        f.write(str(new_circuit))

if __name__ == '__main__':
    generate()
