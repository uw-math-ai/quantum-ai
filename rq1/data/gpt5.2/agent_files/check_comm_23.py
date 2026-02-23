import stim

stabilizers = [
    "IXIIXIIXXXXXIIIIIIIIIIX",
    "XIIXIIXXXXXIIIIIIIIIIXI",
    "IXXIXXXIIIXXIIIIIIIIXII",
    "XXIXXXIIIXXIIIIIIIIXIII",
    "XXXXIIXIIXXIIIIIIXIIII",
    "XIXIXIXXXIIXIIIIIXIIIII",
    "IIIXXXXIXXIXIIIIXIIIIII",
    "IIXXXXIXXIXIIIIXIIIIIII",
    "IXXXXIXXIXIIIIXIIIIIIII",
    "XXXXIXXIXIIIIXIIIIIIIII",
    "XIXIIXIIXXXXXIIIIIIIIII",
    "IZIIZIIZZZZZIIIIIIIIIIZ",
    "ZIIZIIZZZZZIIIIIIIIIIZI",
    "IZZIZZZIIIZZIIIIIIIIZII",
    "ZZIZZZIIIZZIIIIIIIIZIII",
    "ZZZZIIIZIIZZIIIIIIZIIII",
    "ZIZIZIZZZIIZIIIIIZIIIII",
    "IIIZZZZIZZIZIIIIZIIIIII",
    "IIZZZZIZZIZIIIIZIIIIIII",
    "IZZZZIZZIZIIIIZIIIIIIII",
    "ZZZZIZZIZIIIIZIIIIIIIII",
    "ZIZIIZIIZZZZZIIIIIIIIII"
]

# Check commutativity
for i in range(len(stabilizers)):
    for j in range(i + 1, len(stabilizers)):
        s1 = stim.PauliString(stabilizers[i])
        s2 = stim.PauliString(stabilizers[j])
        if not s1.commutes(s2):
            print(f"Stabilizer {i} anticommutes with {j}")

# Try to find a maximal commuting set
def find_maximal_commuting_set(stabs):
    commuting_set = []
    skipped = []
    for i, s_str in enumerate(stabs):
        s = stim.PauliString(s_str)
        commutes_with_all = True
        for existing in commuting_set:
            if not s.commutes(existing):
                commutes_with_all = False
                break
        
        if commutes_with_all:
            commuting_set.append(s)
        else:
            skipped.append(i)
            
    return commuting_set, skipped

commuting_stabs, skipped_indices = find_maximal_commuting_set(stabilizers[:4] + stabilizers[5:])
print(f"Skipped indices (relative to modified list): {skipped_indices}")
print(f"Kept {len(commuting_stabs)} out of {len(stabilizers)-1}")

if len(commuting_stabs) > 0:
    tableau = stim.Tableau.from_stabilizers(commuting_stabs, allow_underconstrained=True)
    circuit = tableau.to_circuit(method="elimination")
    print("\nGenerated Circuit (skipping index 4):")
    print(circuit)
