import stim

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [l.strip() for l in lines if l.strip()]

def main():
    stabs = load_stabilizers('data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt')
    if not stabs:
        print('No stabilizers found.')
        return
    print(f'Number of stabilizers: {len(stabs)}')

    if not stabs:
        return

    stab_len = len(stabs[0])
    print(f'Stabilizer length: {stab_len}')
    
    used_qubits = set()
    for s in stabs:
        if len(s) != stab_len:
            print(f'Error: Stabilizer length mismatch {len(s)} vs {stab_len}')
        for i, char in enumerate(s):
            if char in 'XYZ':
                used_qubits.add(i)
                
    print(f'Qubits involved in stabilizers: {len(used_qubits)}')
    if used_qubits:
        print(f'Max qubit index in stabilizers: {max(used_qubits)}')
    
    # Check circuit
    with open('data/gemini-3-pro-preview/agent_files_ft/circuit.stim', 'r') as f:
        circ_text = f.read()
        # Parse circuit to find max qubit
        try:
            circuit = stim.Circuit(circ_text)
            print(f'Circuit num_qubits: {circuit.num_qubits}')
        except Exception as e:
            print(f'Error parsing circuit: {e}')

if __name__ == '__main__':
    main()
