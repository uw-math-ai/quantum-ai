import stim

with open("problem_stabs.txt", "r") as f:
    content = f.read()

stabilizers = [s.strip() for s in content.split(",") if s.strip()]

try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    with open("circuit_solution.stim", "w") as f:
        f.write(str(circuit))
    print(circuit)
except Exception as e:
    print(e)
