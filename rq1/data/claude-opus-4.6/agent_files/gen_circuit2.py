import stim

# Define stabilizers for 15 qubits
stabilizers = [
    "IIIIIIIXXXXXXXX",  # X on 7-14
    "IIIXXXXIIIIXXXX",  # X on 3-6, 11-14
    "IXXIIXXIIXXIIXX",  # X on 1-2, 5-6, 9-10, 13-14
    "XIXIXIXIXIXIXIX",  # X on 0, 2, 4, 6, 8, 10, 12, 14
    "IIIIIIIZZZZZZZZ",  # Z on 7-14
    "IIIZZZZIIIIZZZZ",  # Z on 3-6, 11-14
    "IZZIIZZIIZZIIZZ",  # Z on 1-2, 5-6, 9-10, 13-14
    "ZIZIZIZIZIZIZIZ",  # Z on 0, 2, 4, 6, 8, 10, 12, 14
]

# Convert to stim PauliStrings
pauli_strings = [stim.PauliString(s) for s in stabilizers]

# Create tableau from stabilizers
print("Creating tableau...")
tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True)

# Get graph_state circuit (produces CZ gates instead of CX)
circuit_graph = tableau.to_circuit(method='graph_state')
print(f"Graph state circuit:\n{circuit_graph}")

# RX on |0> is equivalent to H (ignoring global phase), so we can replace RX with H
# Let's try to process the circuit to work from |0> state
circuit_str = str(circuit_graph)

# Replace RX with H (RX on |0> prepares |+> state, same as H on |0>)
circuit_from_zero = circuit_str.replace("RX", "H")
print(f"\nCircuit from |0> state (replacing RX with H):\n{circuit_from_zero}")

# Let's verify this works
print("\n--- Verifying ---")
test_circuit = stim.Circuit(circuit_from_zero)
print(f"Test circuit parses: {test_circuit}")
