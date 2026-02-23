import stim
import sys
import os

def check_stabilizers(filename):
    print(f'Reading {filename}')
    with open(filename, 'r') as f:
        lines = [l.strip().replace(',', '') for l in f if l.strip()]

    print(f'Loaded {len(lines)} stabilizers.')
    
    # Convert to PauliStrings
    paulis = [stim.PauliString(l) for l in lines]

    # Check commutativity
    try:
        # allow_underconstrained=True is important as we have 132 stabs for 133 qubits
        t = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        print('Successfully created Tableau from stabilizers!')
        
        # If successful, we can just output the circuit
        circ = t.to_circuit()
        print('Circuit generated.')
        
        out_path = 'data/gemini-3-pro-preview/agent_files/circuit_133.stim'
        with open(out_path, 'w') as f:
            f.write(str(circ))
        print(f'Wrote circuit to {out_path}')
            
    except Exception as e:
        print(f'Error creating Tableau: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_stabilizers('data/gemini-3-pro-preview/agent_files/stabilizers_133.txt')

