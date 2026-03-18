import stim

def main():
    # Load baseline
    with open('baseline_job.stim', 'r') as f:
        baseline_text = f.read()
    
    baseline = stim.Circuit(baseline_text)
    
    # Simulate to get tableau
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize graph state circuit
    # method='graph_state' is optimal for CX count
    candidate = tableau.to_circuit(method='graph_state')
    
    # Replace RX with H (if any) to ensure unitary from |0>
    final_circuit = stim.Circuit()
    for instr in candidate:
        if instr.name == "RX":
            final_circuit.append("H", instr.targets_copy())
        else:
            final_circuit.append(instr)
            
    print(final_circuit)

if __name__ == '__main__':
    main()
