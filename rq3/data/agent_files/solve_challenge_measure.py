import stim

def solve():
    with open('target_stabilizers_challenge.txt', 'r') as f:
        # Truncate to 92
        lines = [l.strip()[:92] for l in f if l.strip()]
    
    paulis = [stim.PauliString(l) for l in lines]
    
    sim = stim.TableauSimulator()
    # Start with |0...0> (default)
    
    # Measure each stabilizer to project the state
    # This prepares a state stabilized by the compatible subset
    # Later measurements override earlier ones if they anticommute
    for s in paulis:
        sim.measure_observable(s)
        
    # Get the resulting state tableau
    tableau = sim.current_inverse_tableau()
    
    # Synthesize circuit
    circuit = tableau.to_circuit(method='graph_state')
    
    # Check metrics
    cx = 0
    cz = 0
    for instr in circuit:
        if instr.name == 'CX': cx += 1
        if instr.name == 'CZ': cz += 1
    print(f"Synthesized circuit has {cx} CX and {cz} CZ.")
    
    # Decompose and save
    new_circuit = stim.Circuit()
    for instruction in circuit:
        # Same filtering as before
        name = instruction.name
        targets = instruction.targets_copy()
        if name in ['R', 'RZ', 'TICK']: continue
        if name in ['M', 'MX', 'MY', 'MZ']: continue # Should not happen from to_circuit
        
        if name == 'RX':
            new_circuit.append('H', targets)
        elif name == 'RY':
            new_circuit.append('H', targets)
            new_circuit.append('S', targets)
        else:
            new_circuit.append(name, targets)
            
    with open('candidate_measure.stim', 'w') as f:
        for instruction in new_circuit:
            if instruction.name in ['CZ', 'CX', 'CY', 'SWAP']:
                targets = instruction.targets_copy()
                for i in range(0, len(targets), 2):
                    f.write(f"{instruction.name} {targets[i].value} {targets[i+1].value}\n")
            elif instruction.name in ['H', 'S', 'X', 'Y', 'Z', 'I']:
                targets = instruction.targets_copy()
                for t in targets:
                     f.write(f"{instruction.name} {t.value}\n")
            else:
                f.write(str(instruction) + "\n")

    print("Saved candidate_measure.stim")

if __name__ == "__main__":
    solve()
