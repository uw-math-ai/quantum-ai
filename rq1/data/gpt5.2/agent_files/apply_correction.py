import stim

# Load clean graph circuit
with open("circuit_54_graph_clean.stim", "r") as f:
    circuit_text = f.read()

circuit = stim.Circuit(circuit_text)

# Correction string from previous step
correction_str = "ZIIZIIZIIIIIIIIIIIIIIIIIIIIIIZIIIIIIIIIIIIIIIIIIIIIIII"

# Find indices where it is Z
z_indices = []
for i, c in enumerate(correction_str):
    if c == "Z":
        z_indices.append(i)
    elif c == "X":
        # Should not happen based on output, but handled
        pass

print(f"Applying Z to indices: {z_indices}")

# Append Z gates
if z_indices:
    circuit.append("Z", z_indices)

# Save to circuit_54_corrected.stim
with open("circuit_54_corrected.stim", "w") as f:
    f.write(str(circuit))
    
print("Saved circuit_54_corrected.stim")
