import stim
import sys
import os

def solve():
    try:
        # Load stabilizers
        filepath = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_133.txt"
        with open(filepath, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        stabilizers = lines
        num_qubits = len(stabilizers[0])
        
        print(f"Number of qubits: {num_qubits}")
        print(f"Number of stabilizers: {len(stabilizers)}")

        # Check for consistency
        try:
            tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
            circuit = tableau.to_circuit()
            
            output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_133.stim"
            with open(output_path, "w") as f:
                f.write(str(circuit))
            print("Circuit generated successfully.")
            
        except Exception as e:
            print(f"Error generating tableau: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    solve()
