import stim
import sys

# Target stabilizers
stabilizers_str = [
    "IIXIXXX", 
    "IXIXIXX", 
    "XXXIIXI", 
    "IIZIZZZ", 
    "IZIZIZZ", 
    "ZZZIIZI"
]

def solve():
    ps = []
    for s in stabilizers_str:
        try:
            ps.append(stim.PauliString(s))
        except Exception as e:
            print(f"Error parsing stabilizer {s}: {e}")
            return

    try:
        # Create a Tableau from stabilizers
        # allow_underconstrained=True allows finding a state even if generators are not maximal set
        tableau = stim.Tableau.from_stabilizers(ps, allow_underconstrained=True)
        
        # Convert to circuit using 'elimination' method
        circuit = tableau.to_circuit("elimination")
        
        # Print the circuit to a file
        with open("circuit_solution.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated and saved to circuit_solution.stim")
        print(circuit)
        
    except Exception as e:
        print(f"Error creating tableau: {e}")
        sys.exit(1)

if __name__ == "__main__":
    solve()
