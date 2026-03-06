
import stim

stabilizers = [
    "XZZXIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXX",
    "ZZZZZZZZZZZZZZZZZZZZ"
]

def check_commutativity(stabs):
    parsed = [stim.PauliString(s) for s in stabs]
    anticommuting_pairs = []
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            if parsed[i].commutes(parsed[j]) == False:
                anticommuting_pairs.append((i, j))
    return anticommuting_pairs

pairs = check_commutativity(stabilizers)
if pairs:
    print("Found anticommuting pairs:")
    for i, j in pairs:
        print(f"  {i} ({stabilizers[i]}) vs {j} ({stabilizers[j]})")
else:
    print("All stabilizers commute.")
