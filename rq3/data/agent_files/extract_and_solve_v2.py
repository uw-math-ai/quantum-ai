import stim
import sys

# Load baseline
try:
    with open("my_baseline_v2.stim") as f:
        baseline = stim.Circuit(f.read())
except Exception as e:
    sys.stderr.write(f"Error loading baseline: {e}")
    sys.exit(1)

tableau = stim.Tableau.from_circuit(baseline)
n = len(tableau)

stabilizers = []
for i in range(n):
    s = tableau.z_output(i)
    stabilizers.append(s)

try:
    new_tableau = stim.Tableau.from_stabilizers(
        stabilizers,
        allow_redundant=True,
        allow_underconstrained=True
    )
    circuit = new_tableau.to_circuit(method="graph_state")
    print(circuit)
    
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)
