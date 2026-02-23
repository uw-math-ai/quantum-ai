import stim
import sys
import os

def solve():
    # Read stabilizers from file
    stab_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_105.txt"
    try:
        with open(stab_path, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print(f"Error: File not found at {stab_path}")
        return

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        clean_line = line.replace(",", "")
        stabilizers.append(stim.PauliString(clean_line))

    if not stabilizers:
        print("No stabilizers found.")
        return

    # Check qubit count
    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {len(stabilizers)}")

    # Create tableau
    try:
        # allow_underconstrained=True because we might have fewer stabilizers than qubits
        # allow_redundant=True just in case
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        print("Tableau created.")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Convert to circuit
    try:
        # Using "elimination" is standard for finding a preparation circuit
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully.")
        
        # Output circuit to file
        out_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_105.stim"
        with open(out_path, "w") as f:
            f.write(str(circuit))
        print(f"Circuit written to {out_path}")
            
    except Exception as e:
        print(f"Error converting to circuit: {e}")

if __name__ == "__main__":
    solve()
