import stim
import itertools

# Available single qubit gates in Stim
# H, S, S_DAG, X, Y, Z, SQRT_X, SQRT_X_DAG, SQRT_Y, SQRT_Y_DAG
# Also include I
PRIMITIVES = ["I", "H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]

def get_tableau_str(seq):
    c = stim.Circuit()
    for g in seq:
        if g != "I": c.append(g, [0])
    return str(stim.Tableau.from_circuit(c))

LOOKUP = {}

def build_lookup():
    # Breadth First Search for shortest sequences
    # Length 0
    LOOKUP[get_tableau_str([])] = []
    
    # Length 1
    for g in PRIMITIVES:
        if g == "I": continue
        s = get_tableau_str([g])
        if s not in LOOKUP: LOOKUP[s] = [g]
        
    # Length 2
    for g1 in PRIMITIVES:
        for g2 in PRIMITIVES:
            if g1 == "I" or g2 == "I": continue
            seq = [g1, g2]
            s = get_tableau_str(seq)
            if s not in LOOKUP: LOOKUP[s] = seq

build_lookup()

ops = {i: [] for i in range(12)}

# Parsed from candidate.stim (AFTER CZ):
# X 4
ops[4].append("X")
# Y 0 9 10
for q in [0, 9, 10]: ops[q].append("Y")
# Z 1 3 5 6 8
for q in [1, 3, 5, 6, 8]: ops[q].append("Z")
# S 3 9
for q in [3, 9]: ops[q].append("S")
# H 0 1 2 4 5 7 8
for q in [0, 1, 2, 4, 5, 7, 8]: ops[q].append("H")
# S 2 8
for q in [2, 8]: ops[q].append("S")

for q in range(12):
    seq = ops[q]
    s = get_tableau_str(seq)
    if s in LOOKUP:
        opt = LOOKUP[s]
        print(f"Q{q}: {seq} -> {opt}")
    else:
        print(f"Q{q}: {seq} -> NOT FOUND (len > 2?)")
