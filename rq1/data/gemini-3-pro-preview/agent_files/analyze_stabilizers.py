import stim
import numpy as np

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f]
    return [l for l in lines if l]

def check_commutation(stabilizers):
    ps = [stim.PauliString(s) for s in stabilizers]
    n = len(ps)
    commutes = True
    for i in range(n):
        for j in range(i + 1, n):
            if not ps[i].commutes(ps[j]):
                print(f"Stabilizers {i} and {j} anti-commute!")
                commutes = False
                return False
    return True

stabilizers = load_stabilizers("data/gemini-3-pro-preview/agent_files/stabilizers_current.txt")
print(f"Number of stabilizers: {len(stabilizers)}")
if len(stabilizers) > 0:
    print(f"Length of stabilizer: {len(stabilizers[0])}")

if check_commutation(stabilizers):
    print("All stabilizers commute.")
    try:
        # stim.Tableau.from_stabilizers creates a Tableau that has these stabilizers
        # If underconstrained, it fills in the rest.
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        print("Circuit successfully generated from Tableau.")
        with open("data/gemini-3-pro-preview/agent_files/circuit_candidate.stim", "w") as f:
            f.write(str(circuit))
    except Exception as e:
        print(f"Error generating Tableau: {e}")
else:
    print("Stabilizers do not commute, cannot use simple Tableau construction.")
