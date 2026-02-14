import stim
import os

def solve():
    file_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_81_v2.txt"
    with open(file_path, "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    # Verify lengths
    for i, s in enumerate(stabs):
        if len(s) != 81:
            print(f"Error: Stabilizer {i} length {len(s)} != 81. String: {s}")
            return

    try:
        print(f"Number of stabilizers: {len(stabs)}")
        
        # Create a tableau from the stabilizers
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
        
        # Convert to circuit
        circuit = tableau.to_circuit(method='elimination')
        
        print("Circuit generated successfully.")
        
        # Save to file
        output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_81_v2.stim"
        with open(output_path, "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
