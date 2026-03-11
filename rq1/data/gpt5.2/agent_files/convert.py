import stim

# Read the circuit
with open("data/gpt5.2/agent_files/candidate_v1.stim", "r") as f:
    circuit_str = f.read()

# Replace RX with H for each qubit (since we start from |0>)
# RX prepares |+>, which is H|0>
lines = circuit_str.strip().split("\n")
new_lines = []
for line in lines:
    if line.startswith("RX "):
        # Replace RX with H
        qubits = line[3:]
        new_lines.append("H " + qubits)
    else:
        new_lines.append(line)

new_circuit_str = "\n".join(new_lines)
print("Converted circuit:")
print(new_circuit_str)

# Save
with open("data/gpt5.2/agent_files/candidate_v2.stim", "w") as f:
    f.write(new_circuit_str)
