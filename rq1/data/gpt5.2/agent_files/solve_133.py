import stim
import sys

def solve():
    try:
        with open('stabilizers_133.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        stabilizers = [stim.PauliString(line) for line in lines]
        
        # Create tableau
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # Convert to circuit
        circuit = tableau.to_circuit('elimination')
        
        print('Circuit generated successfully.')
        with open('circuit_133.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    solve()
