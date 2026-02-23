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

print("Checking commutativity...")
for i in range(len(stabilizers)):
    for j in range(i + 1, len(stabilizers)):
        if not stabilizers[i].commutes(stabilizers[j]):
            print(f"Anticommute: {i} {j}")

try:
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    print("Circuit:")
    print(circuit)
except Exception as e:
    print(e)
