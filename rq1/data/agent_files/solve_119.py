import stim
import sys

def solve():
    print("Reading stabilizers...")
    try:
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\target_stabilizers_119.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"Number of stabilizers: {len(lines)}")
    if not lines:
        print("No stabilizers found.")
        return

    n = len(lines[0])
    print(f"Number of qubits (from length): {n}")
    
    # Check if all have same length
    for i, line in enumerate(lines):
        if len(line) != n:
            print(f"Error: Line {i} has length {len(line)}, expected {n}")
            return

    # Try to create tableau
    try:
        stabilizers = [stim.PauliString(s) for s in lines]
        # In newer versions of stim, use `stim.Tableau.from_stabilizers`
        # Check if allow_underconstrained is supported
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        print("Successfully created tableau from stabilizers!")
        
        # Convert to circuit
        circuit = tableau.to_circuit()
        
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\circuit_119.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    solve()
