import stim

# Read the circuit and replace RX with H
with open("data/claude-opus-4.6/agent_files/candidate_current.stim", "r") as f:
    circuit_text = f.read()

# Replace RX with H
circuit_text = circuit_text.replace("RX ", "H ")

# Parse and output
circuit = stim.Circuit(circuit_text)
print(circuit)

# Save
with open("data/claude-opus-4.6/agent_files/candidate_clean.stim", "w") as f:
    f.write(str(circuit))
