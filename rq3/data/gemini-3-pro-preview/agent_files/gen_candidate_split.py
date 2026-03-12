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
    candidate = tableau.to_circuit(method='graph_state')
    
    # Post-process to split long lines and replace RX
    final_circuit = stim.Circuit()
    for instr in candidate:
        if instr.name == "RX":
            # Replace with H on same targets, split them
            for t in instr.targets_copy():
                final_circuit.append("H", [t])
        elif instr.name == "CZ":
            # Split into pairs
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                final_circuit.append("CZ", [targets[i], targets[i+1]])
        else:
            # Other gates (X, Y, Z, S, H) -> split
            # Note: 2-qubit gates like CX, SWAP need pairs. 
            # Graph state usually only has H, S, X, Y, Z, CZ.
            # CZ is the only 2-qubit gate.
            # Single qubit gates:
            gate_len = 1
            if instr.name in ["CX", "SWAP", "ISWAP", "CZ"]: # just in case
                gate_len = 2
            
            targets = instr.targets_copy()
            for i in range(0, len(targets), gate_len):
                final_circuit.append(instr.name, targets[i:i+gate_len], instr.gate_args_copy())
            
    # Print instructions manually to avoid coalescing
    for instr in final_circuit:
        print(instr)

if __name__ == '__main__':
    main()
