import stim
with open("candidate_synthesis.stim", "r") as f:
    c = stim.Circuit(f.read())
print(f"Num qubits: {c.num_qubits}")
