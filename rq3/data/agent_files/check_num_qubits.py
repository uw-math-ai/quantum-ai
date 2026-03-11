import stim
with open("current_baseline.stim", "r") as f:
    c = stim.Circuit(f.read())
print(f"Num qubits: {c.num_qubits}")
