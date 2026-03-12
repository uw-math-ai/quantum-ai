import stim

stabilizers_text = """
XXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIXXIXXIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIXXIXXIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIII
IIIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIXXIXXIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIXXIXXIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXX
IIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIII
IIIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXII
IIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZI
IZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIII
ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII
IIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZ
IIXXXIIIIIIXXXIIIIIIXXXIIIIIIXXXIIII
ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII
"""

stabilizers = [stim.PauliString(line.strip()) for line in stabilizers_text.strip().splitlines()]

# Attempt to create a tableau from stabilizers
try:
    # allow_underconstrained=True because 34 stabs for 36 qubits
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
except Exception as e:
    print(f"Error creating tableau: {e}")
    exit(1)

# Generate circuit using graph_state method
circuit = tableau.to_circuit(method="graph_state")

# Post-processing:
# Replace RX with H (assuming |0> input)
# Remove RZ/R (reset Z) as they are identity on |0>
new_circuit = stim.Circuit()
for instruction in circuit:
    if instruction.name == "RX":
        targets = instruction.targets_copy()
        new_circuit.append("H", targets)
    elif instruction.name in ["R", "RZ"]:
        # Identity on |0>
        pass
    elif instruction.name == "MY":
        new_circuit.append(instruction)
    elif instruction.name in ["M", "MX", "MZ"]:
        # Should not happen for this task
        new_circuit.append(instruction)
    else:
        new_circuit.append(instruction)

# Output the circuit
with open("candidate_attempt_1.stim", "w") as f:
    f.write(str(new_circuit))
print("Wrote to candidate_attempt_1.stim")
