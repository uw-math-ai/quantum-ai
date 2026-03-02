import stim
import sys
import os

def solve():
    try:
        filepath = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt"
        with open(filepath, "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        lengths = set(len(s) for s in stabilizers)
        if len(lengths) != 1:
            print(f"Error: Stabilizers have different lengths: {lengths}")
            return
            
        num_qubits = list(lengths)[0]
        print(f"Number of qubits: {num_qubits}")
        
        # Check commutativity and consistency using Tableau
        try:
            # We try to create a tableau from the stabilizers.
            # allow_underconstrained=True allows fewer than N stabilizers.
            t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            
            # If successful, we can convert it to a circuit.
            # The circuit prepares the state stabilized by the tableau.
            circuit = t.to_circuit()
            print("Successfully generated circuit.")
            print(circuit)
            
        except ValueError as e:
            print(f"ValueError (likely anticommuting or inconsistent): {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    solve()
