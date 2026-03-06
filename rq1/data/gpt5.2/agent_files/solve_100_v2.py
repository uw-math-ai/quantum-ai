import stim
import sys

def solve():
    # Read stabilizers
    with open('stabilizers_100.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(lines)} stabilizers")
    
    # Convert to Stim PauliStrings
    paulis = []
    for line in lines:
        try:
            paulis.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line: {line}")
            raise e
            
    # Check for commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if paulis[i].commutes(paulis[j]) == False:
                anticommuting_pairs.append((i, j))
                
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} vs {j}")
            
    # Attempt to solve
    try:
        # allow_underconstrained=True allows it to pick arbitrary values for unconstrained degrees of freedom
        # but it will fail if stabilizers are inconsistent (anticommute)
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        print("Successfully generated circuit!")
        
        with open('circuit_100.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Failed to generate circuit: {e}")

if __name__ == "__main__":
    solve()
