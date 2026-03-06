import stim
import sys

def solve():
    print('Starting solution...')
    try:
        with open('data/gemini-3-pro-preview/agent_files/stabilizers_119.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f'Number of stabilizers: {len(lines)}')
        
        # Convert strings to PauliStrings
        print('Converting to PauliStrings...')
        pauli_strings = []
        for i, line in enumerate(lines):
            try:
                ps = stim.PauliString(line)
                pauli_strings.append(ps)
            except Exception as e:
                print(f'Error converting line {i}: {line}')
                print(e)
                return

        # Create tableau from stabilizers
        print('Creating tableau...')
        try:
            # allow_redundant=True in case they are not independent
            # allow_underconstrained=True in case there are fewer than N stabilizers
            t = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
            print('Successfully created tableau from stabilizers.')
            
            # Convert to circuit
            circuit = t.to_circuit()
            
            # Output the circuit to a file
            with open('data/gemini-3-pro-preview/agent_files/circuit_119.stim', 'w') as f:
                f.write(str(circuit))
                
            print('Circuit generated and saved to data/gemini-3-pro-preview/agent_files/circuit_119.stim')
            
        except ValueError as ve:
             print(f'ValueError creating tableau: {ve}')
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    solve()