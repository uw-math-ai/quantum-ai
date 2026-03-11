import stim

# Read the generated circuit
with open("data/claude-opus-4.6/agent_files/candidate.stim", "r") as f:
    circuit_text = f.read()

# Replace RX with H (RX resets to |+⟩, but starting from |0⟩ we use H to get |+⟩)
lines = circuit_text.strip().split('\n')
new_lines = []
for line in lines:
    if line.startswith("RX "):
        # Extract qubits and replace RX with H
        qubits = line[3:]
        new_lines.append(f"H {qubits}")
    else:
        new_lines.append(line)

clean_circuit_text = '\n'.join(new_lines)
print("Clean circuit:")
print(clean_circuit_text)

# Parse and verify
circuit = stim.Circuit(clean_circuit_text)
print(f"\nCircuit has {len(circuit)} instructions")

# Save the clean circuit
with open("data/claude-opus-4.6/agent_files/candidate_clean.stim", "w") as f:
    f.write(clean_circuit_text)

print("\nSaved to candidate_clean.stim")
