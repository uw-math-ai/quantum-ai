import stim

with open("target_stabilizers_rq3_new_v5.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Number of lines: {len(lines)}")
lengths = [len(l) for l in lines]
print(f"Lengths: {min(lengths)} to {max(lengths)}")

s = stim.PauliString(lines[0])
print(f"First stabilizer length: {len(s)}")

t = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in lines], allow_redundant=True, allow_underconstrained=True)
print(f"Tableau size: {len(t)}")
c = t.to_circuit(method="graph_state")
print(f"Circuit num qubits: {c.num_qubits}")
