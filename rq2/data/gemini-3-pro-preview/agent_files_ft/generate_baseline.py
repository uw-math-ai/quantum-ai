import stim
import sys

# Read stabilizers
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Read {len(lines)} stabilizers")
if len(lines) > 0:
    print(f"Length of first stabilizer: {len(lines[0])}")

# Create tableau
try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_redundant=True, allow_underconstrained=True)
    print("Tableau created successfully")
    
    # Synthesize circuit
    # Graph state method is usually most compact for stabilizer states
    circuit = tableau.to_circuit(method="graph_state")
    
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\baseline.stim", "w") as f:
        f.write(str(circuit))
        
    print(f"Baseline circuit generated with {len(circuit)} instructions")
    
except Exception as e:
    print(f"Error: {e}")
