import stim

stabilizers = [
    "IXIIXIIXXXXXIIIIIIIIIIX",
    "XIIXIIXXXXXIIIIIIIIIIXI",
    "IXXIXXXIIIXXIIIIIIIIXII",
    "XXIXXXIIIXXIIIIIIIIXIII",
    # "XXXXIIXIIXXIIIIIIXIIII", # S4
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

s4_short = "XXXXIIXIIXXIIIIIIXIIII"

candidates = []
chars = ['I', 'X'] # Assume it's I or X based on context
for char in chars:
    for pos in range(len(s4_short) + 1):
        cand = s4_short[:pos] + char + s4_short[pos:]
        
        # Check against ALL other stabilizers
        all_commute = True
        cand_p = stim.PauliString(cand)
        for s in stabilizers:
            if not cand_p.commutes(stim.PauliString(s)):
                all_commute = False
                break
        
        if all_commute:
            candidates.append(cand)

print(f"Candidates that commute with ALL: {len(candidates)}")
for c in candidates:
    print(c)
