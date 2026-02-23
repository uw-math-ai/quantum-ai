import stim

def solve():
    try:
        with open('data/gemini-3-pro-preview/agent_files/stabilizers_119.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f'Number of stabilizers: {len(lines)}')
        
        # Convert strings to PauliStrings
        pauli_strings = [stim.PauliString(line) for line in lines]

        # Create tableau from stabilizers
        # allow_redundant=True in case they are not independent
        # allow_underconstrained=True in case there are fewer than N stabilizers
        t = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        print('Successfully created tableau from stabilizers.')
        
        # Convert to circuit
        circuit = t.to_circuit()
        
        # Output the circuit to a file
        with open('data/gemini-3-pro-preview/agent_files/circuit_119.stim', 'w') as f:
            f.write(str(circuit))
            
        print('Circuit generated and saved.')
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    solve()
