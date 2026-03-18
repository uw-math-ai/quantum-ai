import stim
import sys

def solve():
    print("Loading baseline...")
    with open('baseline_task.stim', 'r') as f:
        baseline = stim.Circuit(f.read())
    
    # Get the tableau of the unitary transformation
    print("Computing tableau...")
    tableau = stim.Tableau.from_circuit(baseline)
    
    # Convert to graph state circuit
    print("Synthesizing graph state circuit...")
    circuit = tableau.to_circuit(method='graph_state')
    
    # Replace RX with H
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == 'RX':
            new_circuit.append('H', instr.targets_copy())
        else:
            new_circuit.append(instr)
            
    with open('candidate_graph_v4.stim', 'w') as f:
        f.write(str(new_circuit))
    print("Done.")

if __name__ == "__main__":
    solve()
