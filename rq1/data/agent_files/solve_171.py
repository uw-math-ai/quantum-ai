import stim
import sys

def solve():
    # Read stabilizers from file
    with open('stabilizers_171.txt', 'r') as f:
        lines = f.readlines()
    
    stabs = [line.strip() for line in lines if line.strip()]
    
    # Create tableau from stabilizers
    try:
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
        circuit = tableau.to_circuit('elimination')
        print(circuit)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    solve()
