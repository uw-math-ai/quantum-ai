import stim

stabilizers = [
    "XXIIXXI",
    "XIXIXIX",
    "IIIXXXX",
    "ZZIIZZI",
    "ZIZIZIZ",
    "IIIZZZZ"
]

def check_commutativity(stabs):
    n = len(stabs)
    for i in range(n):
        for j in range(i + 1, n):
            s1 = stabs[i]
            s2 = stabs[j]
            anticommutes = False
            count = 0
            for k in range(len(s1)):
                p1 = s1[k]
                p2 = s2[k]
                if (p1 == 'X' and p2 == 'Z') or (p1 == 'Z' and p2 == 'X'):
                    count += 1
            if count % 2 == 1:
                print(f"Stabilizers {i} and {j} anticommute!")
                return False
    print("All stabilizers commute.")
    return True

check_commutativity(stabilizers)

# Try to find a circuit using stim's Tableau
try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    with open("circuit_7.stim", "w") as f:
        f.write(str(circuit))
    print("Circuit saved to circuit_7.stim")
except Exception as e:
    print(f"Error finding circuit: {e}")
