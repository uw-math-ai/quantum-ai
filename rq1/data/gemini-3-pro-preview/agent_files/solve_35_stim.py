import stim
import sys

# Load corrected stabilizers
try:
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_35_corrected.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("Error: Corrected stabilizers file not found.")
    sys.exit(1)

# Create Stim Tableau
try:
    stim_stabs = [stim.PauliString(s) for s in stabilizers]
    # allow_underconstrained=True because 34 stabs for 35 qubits
    tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_redundant=True, allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    
    # Save circuit to file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_35.stim", "w") as f:
        f.write(str(circuit))
        
    print("Circuit generated successfully.")
except Exception as e:
    print(f"Error creating tableau: {e}")
