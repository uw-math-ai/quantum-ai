import stim
s = ["X" * 150]
t = stim.Tableau.from_stabilizers([stim.PauliString(x) for x in s], allow_underconstrained=True)
print(f"Tableau size: {len(t)}")
c = t.to_circuit("elimination")
print(f"Circuit qubits: {c.num_qubits}")
