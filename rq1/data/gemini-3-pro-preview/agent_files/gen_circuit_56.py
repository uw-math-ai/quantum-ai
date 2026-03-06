import stim
import sys

# Load stabilizers
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_56.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

paulis = [stim.PauliString(line) for line in lines]

# Create tableau
try:
    t = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
    circuit = t.to_circuit()
    
    # Save circuit to file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\candidate_56.stim", "w") as f:
        f.write(str(circuit))
        
    print("Circuit generated.")

except Exception as e:
    print(f"Error: {e}")
