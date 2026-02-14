import stim
import sys

def solve():
    print("Reading stabilizers...")
    with open("stabilizers_133.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(lines)} stabilizers.")
    if len(lines) == 0:
        print("No stabilizers found!")
        return

    # Check length
    n_qubits = len(lines[0])
    print(f"Number of qubits: {n_qubits}")
    
    stabilizers = []
    for line in lines:
        if len(line) != n_qubits:
            print(f"Error: Stabilizer length mismatch. Expected {n_qubits}, got {len(line)}")
            return
        stabilizers.append(stim.PauliString(line))
        
    print("Checking commutation...")
    # This might be slow if there are many. 
    # For now, let's trust stim to check it or just try to build the tableau.
    
    try:
        print("Constructing tableau...")
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        print("Converting to circuit...")
        # 'elimination' method generates a circuit that prepares the state from |0>
        # It uses Gaussian elimination.
        c = t.to_circuit("elimination")
        
        print(f"Circuit generated with {len(c)} instructions.")
        
        with open("circuit_133.stim", "w") as f:
            f.write(str(c))
            
        print("Circuit saved to circuit_133.stim")
        
    except Exception as e:
        print(f"Error building tableau: {e}")

if __name__ == "__main__":
    solve()
