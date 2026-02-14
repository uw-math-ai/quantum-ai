import stim
import os

def solve():
    # Use absolute paths
    base_dir = r"C:\Users\anpaz\Repos\quantum-ai\rq1"
    stabs_path = os.path.join(base_dir, "target_stabilizers_119_v4.txt")
    out_path = os.path.join(base_dir, "circuit_119_v4.stim")

    print(f"Reading from {stabs_path}")
    with open(stabs_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabs = [stim.PauliString(line) for line in lines if set(line).issubset({'I', 'X', 'Y', 'Z'})]
    print(f"Loaded {len(stabs)} stabilizers.")
    
    try:
        # Create the tableau from stabilizers
        # allow_underconstrained=True because we might have fewer stabilizers than qubits
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
        
        # Convert to circuit using elimination method
        circuit = tableau.to_circuit("elimination")
        
        # Write the circuit to a file
        with open(out_path, 'w') as f:
            f.write(str(circuit))
            
        print(f"Circuit generated successfully: {out_path}")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
