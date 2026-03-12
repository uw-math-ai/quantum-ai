import stim

def generate():
    print('Loading stabilizers...')
    try:
        with open('current_stabilizers.txt', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print('Error: current_stabilizers.txt not found')
        return

    # Replace commas with spaces and split
    parts = content.replace(',', ' ').split()
    
    stabilizers = []
    for p in parts:
        p = p.strip()
        if p:
            try:
                stabilizers.append(stim.PauliString(p))
            except Exception as e:
                print(f'Error parsing stabilizer: {p} -> {e}')
                return
            
    print(f'Loaded {len(stabilizers)} stabilizers.')

    # Create Tableau
    print('Creating Tableau from stabilizers...')
    try:
        # allow_redundant=True, allow_underconstrained=True handles duplicate/subset stabilizers
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f'Error creating tableau: {e}')
        return

    # Synthesize graph state
    print('Synthesizing graph state...')
    try:
        candidate = tableau.to_circuit(method='graph_state')
    except Exception as e:
        print(f'Error synthesizing graph state: {e}')
        return
    
    new_circuit = stim.Circuit()
    for instruction in candidate:
        if instruction.name == 'RX':
            targets = instruction.targets_copy()
            new_circuit.append('H', targets)
        elif instruction.name in ['R', 'RZ', 'RY']:
            # Ignore resets
            pass
        else:
            new_circuit.append(instruction)

    # Save candidate
    print('Saving candidate_from_stabs.stim...')
    with open('candidate_from_stabs.stim', 'w') as f:
        f.write(str(new_circuit))

if __name__ == '__main__':
    generate()
