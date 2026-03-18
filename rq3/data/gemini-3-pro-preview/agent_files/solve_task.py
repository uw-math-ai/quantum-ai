import stim

stabilizers = [
    stim.PauliString("IIIIIIIXXXXXXXX"),
    stim.PauliString("IIIXXXXIIIIXXXX"),
    stim.PauliString("IXXIIXXIIXXIIXX"),
    stim.PauliString("XIXIXIXIXIXIXIX"),
    stim.PauliString("IIIIIIIZZZZZZZZ"),
    stim.PauliString("IIIZZZZIIIIZZZZ"),
    stim.PauliString("IZZIIZZIIZZIIZZ"),
    stim.PauliString("ZIZIZIZIZIZIZIZ")
]

# Create tableau from stabilizers
# allow_underconstrained=True because 8 stabilizers for 15 qubits (7 logicals)
tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)

# Synthesis method 'graph_state' is optimal for CX count (uses CZs)
circuit = tableau.to_circuit(method="graph_state")

# Write to file and clean up
circuit_str = str(circuit)
circuit_str = circuit_str.replace("RX", "H")
circuit_str = circuit_str.replace("TICK\n", "")

with open("candidate.stim", "w") as f:
    f.write(circuit_str)

print("Candidate generated with graph_state method and cleaned.")
