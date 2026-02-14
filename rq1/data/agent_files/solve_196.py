import stim
import sys

def solve():
    # Read stabilizers
    with open('target_stabilizers_196.txt', 'r') as f:
        content = f.read()
    
    # Split by comma or newline
    import re
    tokens = re.split(r'[,\n]+', content)
    
    # Clean up tokens
    lines = [t.strip() for t in tokens if t.strip()]

    
    # Create PauliStrings
    stabilizers = []
    seen = set()
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line: {line}")
            print(e)
            return

    # Create tableau from stabilizers
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Generate circuit
    circuit = tableau.to_circuit('elimination')
    
    # Write circuit to file
    with open('circuit_196.stim', 'w') as f:
        f.write(str(circuit))
        
    print("Circuit generated successfully.")

if __name__ == "__main__":
    solve()