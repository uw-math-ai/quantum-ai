import stim

# Reconstruct corrected stabilizers
stabilizers = []
patterns = [
    "IIXIXXX", "IXIXIXX", "XXXIIXI",
    "IIZIZZZ", "IZIZIZZ", "ZZZIIZI"
]

for pattern in patterns:
    for i in range(7):
        prefix = "I" * (i * 7)
        suffix = "I" * (49 - (i * 7) - 7)
        stab = prefix + pattern + suffix
        stabilizers.append(stab)

extras = [
    "IIIIIIIIIIIIIIXXIXIIIIIIIIIIXXIXIIIXXIXIIIXXIXIII",
    "IIIIIIIXXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXIIIXXIXIII",
    "XXIXIIIXXIXIIIXXIXIIIIIIIIIIIIIIIIIXXIXIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIZZIZIIIZZIZIII",
    "IIIIIIIZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIZZIZIII",
    "ZZIZIIIZZIZIIIZZIZIIIIIIIIIIIIIIIIIZZIZIIIIIIIIII"
]
stabilizers.extend(extras)

# Generate circuit
tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
circuit = tableau.to_circuit("elimination")

with open("circuit_49_final.stim", "w") as f:
    f.write(str(circuit))

with open("stabilizers_49_final_list.txt", "w") as f:
    for s in stabilizers:
        f.write(s + "\n")
