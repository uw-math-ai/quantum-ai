import stim
import numpy as np

stabilizers = [
    "XXIIIXXIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXIIIXXIIIIIIII",
    "IIIIIIXXIIIXXIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXIIIXXII",
    "IIXXIIIXXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIXXIIIXXIIIIII",
    "IIIIIIIIXXIIIXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXIIIXX",
    "IIIIXIIIIXIIIIIIIIIIIIIII",
    "IIIIIXIIIIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIXIIIIXIIIII",   # Index 10
    "IIIIIIIIIIIIIIIXIIIIXIIII", # 11
    "IIIIIZZIIIZZIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZIIIZZIII",
    "IZZIIIZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIZZIIIZZIIIIIII",
    "IIIIIIIZZIIIZZIIIIIIIIIII",  # Index 16
    "IIIIIIIIIIIIIIIIIZZIIIZZI",
    "IIIZZIIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIZZIIIZZIIIII",
    "ZZIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZII",
    "IIZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZ"
]

def check_commutativity():
    paulis = [stim.PauliString(s) for s in stabilizers]
    n = len(paulis)
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
                print(f"Stabilizers {i} and {j} anticommute")
                print(f"  {i}: {stabilizers[i]}")
                print(f"  {j}: {stabilizers[j]}")
    
    if not anticommuting_pairs:
        print("All stabilizers commute.")
    else:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")

if __name__ == "__main__":
    check_commutativity()
