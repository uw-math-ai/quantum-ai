import stim

stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXI", "IXZZXIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXZZXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZX", "XIXZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXIXZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ", "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZXIXZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ", "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
]

# Convert to PauliString objects
pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

# Create tableau
try:
    tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
except Exception as e:
    # If standard from_stabilizers fails, we might need to fill the rest manually or use another method.
    # But usually allow_underconstrained works.
    print(f"Error creating tableau: {e}")
    exit(1)

# Synthesize circuit
circuit = tableau.to_circuit(method="graph_state")

# Post-processing to remove resets if they are not needed (assuming |0> input)
# and replace RX with H if necessary.
# Stim's graph state synthesis often starts with RX (Reset X) to get to |+>.
# Since we start at |0>, RX is equivalent to H.
# RZ is equivalent to Identity (since we are at |0>) but we probably want to keep the H.
# Let's inspect the circuit.

# We will iterate and replace/remove.
new_circuit = stim.Circuit()
for instruction in circuit:
    if instruction.name == "RX":
        # RX resets to |+>. If we are at |0>, H takes us to |+>.
        # So replace RX with H.
        targets = instruction.targets_copy()
        new_circuit.append("H", targets)
    elif instruction.name == "R" or instruction.name == "RZ":
        # R or RZ resets to |0>. If we assume |0> start, this is a no-op.
        pass
    else:
        new_circuit.append(instruction)

with open("candidate_graph.stim", "w") as f:
    f.write(str(new_circuit))
print("Written candidate_graph.stim")
