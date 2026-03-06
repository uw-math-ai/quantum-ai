import stim

def debug():
    try:
        with open('data/gemini-3-pro-preview/agent_files/stabilizers_119.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f'First line: {lines[0]}')
        print(f'First line repr: {repr(lines[0])}')
        
        try:
            ps = stim.PauliString(lines[0])
            print(f'Converted first line to PauliString: {ps}')
        except Exception as e:
            print(f'Error converting first line: {e}')
            
        # Try creating tableau with just one stabilizer
        try:
            t = stim.Tableau.from_stabilizers([ps], allow_underconstrained=True)
            print('Created tableau with one stabilizer')
        except Exception as e:
            print(f'Error creating tableau with one stabilizer: {e}')

        # Try with all
        pauli_strings = [stim.PauliString(line) for line in lines]
        t = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        print('Success with all')

    except Exception as e:
        print(f'Global Error: {e}')

if __name__ == '__main__':
    debug()
