import stim
import os

def solve():
    # Use absolute path for reliability
    base_dir = r"C:\Users\anpaz\Repos\quantum-ai\rq1"
    stabs_path = os.path.join(base_dir, "stabilizers_68.txt")
    
    with open(stabs_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Convert to stim PauliStrings
    stabilizers = []
    for s in lines:
        stabilizers.append(stim.PauliString(s))

    print(f"Loaded {len(stabilizers)} stabilizers.")

    try:
        # Try to create a tableau from the stabilizers
        tableau = stim.Tableau.from_stabilizers(
            stabilizers,
            allow_underconstrained=True,
            allow_redundant=True
        )
        circuit = tableau.to_circuit('elimination')
        
        out_path = os.path.join(base_dir, "circuit_68.stim")
        with open(out_path, 'w') as f:
            f.write(str(circuit))
            
        print("Circuit created successfully.")
        
    except Exception as e:
        print(f"Error creating circuit: {e}")

if __name__ == "__main__":
    solve()
