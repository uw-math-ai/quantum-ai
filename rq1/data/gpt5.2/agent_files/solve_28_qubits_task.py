import stim

stabilizers = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXIIXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXIIXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXIIXXI",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIIXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXX",
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIIZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIZZI",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIIZZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZZZ",
    "XXXIIIIXXXIIIIXXXIIIIXXXIIII",
    "ZZZIIIIZZZIIIIZZZIIIIZZZIIII"
]

print(f"Number of stabilizers: {len(stabilizers)}")

# Convert to PauliStrings
pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

# Check commutativity
commutes = True
for i in range(len(pauli_stabilizers)):
    for j in range(i + 1, len(pauli_stabilizers)):
        if not pauli_stabilizers[i].commutes(pauli_stabilizers[j]):
            print(f"Anticommute: {i} vs {j}")
            commutes = False
            
if not commutes:
    print("Stabilizers do not commute! Cannot generate valid state directly.")
else:
    print("All stabilizers commute.")

try:
    # allow_underconstrained=True because we have 26 stabilizers for 28 qubits (underconstrained by 2)
    tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    
    with open("circuit_28_attempt.stim", "w") as f:
        f.write(str(circuit))
    print("Circuit generated successfully to circuit_28_attempt.stim")
except Exception as e:
    print(f"Error: {e}")
