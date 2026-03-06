import stim
import random
import os

# 1. Write the input files from the prompt
baseline_str = """H 0 4 8
CX 0 4 0 8 0 24 0 33 0 34 24 1 1 24 24 1 1 20 20 2 2 20 20 2
H 32
CX 8 2 32 2 16 3 3 16 16 3 3 33
H 12
CX 12 3 32 3 34 3 4 8 4 33 4 34 32 4 8 5 5 8 8 5 12 6 6 12 12 6 34 7 7 34 34 7 7 28 7 33 28 8 8 28 28 8 24 9 9 24 24 9
H 9 10 11 12 14 15 24 34
CX 9 10 9 11 9 12 9 14 9 15 9 24 9 25 9 32 9 34 9 35 25 10 10 25 25 10 10 21 24 11 11 24 24 11 11 21 32 11 17 12 12 17 17 12 12 33
H 13
CX 13 12 32 12 32 13 13 32 32 13 13 14 13 15 13 17 13 24 13 25 13 34 13 35
H 28
CX 28 13 21 14 14 21 21 14 28 14 32 15 15 32 32 15 28 16 16 28 28 16 16 29 29 17 17 29 29 17 20 18 18 20 20 18
H 18
CX 18 21 18 26 18 29 18 33 26 19 19 26 26 19 19 22 25 20 20 25 25 20 20 22 21 25 21 33 29 22 22 29 29 22 22 25 22 29 29 23 23 29 29 23 33 24 24 33 33 24 24 25 26 24 31 24 35 24 25 30 26 25 31 25 35 25 30 26 26 30 30 26 30 26 31 26 35 26 28 27 27 28 28 27
H 27
CX 27 28 27 32 27 34 27 35 28 29 33 29 29 33 33 29 29 33 32 30 30 32 32 30 30 32 34 31 31 34 34 31 31 32 31 33 31 35 33 32 32 33 33 32 34 33 35 33 35 34
"""

stabilizers_str = """XXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIXXIXXIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIXXIXXIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIII
IIIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIXXIXXIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIXXIXXIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXX
IIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIII
IIIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXII
IIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZI
IZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIII
ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII
IIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZ
IIXXXIIIIIIXXXIIIIIIXXXIIIIIIXXXIIII
ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII
"""

with open("baseline.stim", "w") as f:
    f.write(baseline_str)

with open("stabilizers.txt", "w") as f:
    f.write(stabilizers_str)

# 2. Metric function
def get_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit:
        n_targets = len(instruction.targets_copy())
        if instruction.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            # 2-qubit gates
            count = n_targets // 2
            vol += count
            if instruction.name in ["CX", "CNOT"]:
                cx += count
        else:
            # 1-qubit gates (or others like RESET, MEASURE which we shouldn't have)
            # Annotations like TICK, SHIFT_COORDS have 0 targets or are ignored for volume?
            # "volume – total gate count in the volume gate set"
            # We assume H, S, X, Y, Z, etc count as 1 per target.
            if instruction.name not in ["TICK", "SHIFT_COORDS", "QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE"]:
                 vol += n_targets
    return cx, vol

# 3. Load baseline and get metrics
baseline = stim.Circuit(baseline_str)
base_cx, base_vol = get_metrics(baseline)
print(f"Baseline: CX={base_cx}, Vol={base_vol}")

# 4. Load stabilizers
with open("stabilizers.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

# 5. Search
best_circuit = None
best_cx = base_cx
best_vol = base_vol

# Helper to check improvement
def is_better(c, v):
    if c < base_cx:
        return True
    if c == base_cx and v < base_vol:
        return True
    return False

# Helper to check strictly better than current best
def is_strictly_better_than_best(c, v):
    if c < best_cx:
        return True
    if c == best_cx and v < best_vol:
        return True
    return False

# Strategy: Random permutations of stabilizers + graph_state synthesis
attempts = 500
print(f"Starting search with {attempts} iterations...")

# Also try original order
orders_to_try = [stabilizers]
for _ in range(attempts):
    s_copy = stabilizers.copy()
    random.shuffle(s_copy)
    orders_to_try.append(s_copy)

for i, s_order in enumerate(orders_to_try):
    try:
        # Convert strings to PauliString
        stabilizers_pauli = [stim.PauliString(s) for s in s_order]
        
        # allow_underconstrained=True because we have 34 stabilizers for 36 qubits
        tableau = stim.Tableau.from_stabilizers(stabilizers_pauli, allow_underconstrained=True)
        
        # Try graph state synthesis
        circ_graph = tableau.to_circuit("graph_state")
        c, v = get_metrics(circ_graph)
        
        if best_circuit is None or c < best_cx or (c == best_cx and v < best_vol):
            print(f"Iter {i}: Found Graph State! CX={c}, Vol={v}")
            best_cx = c
            best_vol = v
            best_circuit = circ_graph
            
        # Try elimination synthesis
        circ_elim = tableau.to_circuit("elimination")
        c2, v2 = get_metrics(circ_elim)
        
        if best_circuit is None or c2 < best_cx or (c2 == best_cx and v2 < best_vol):
            print(f"Iter {i}: Found Elimination! CX={c2}, Vol={v2}")
            best_cx = c2
            best_vol = v2
            best_circuit = circ_elim
            
    except Exception as e:
        if i == 0: # Print first error
             print(f"Error in iter {i}: {e}")
        pass

if best_circuit:
    print(f"Best found: CX={best_cx}, Vol={best_vol}")
    with open("best_candidate.stim", "w") as f:
        f.write(str(best_circuit))
    if is_better(best_cx, best_vol):
        print("SUCCESS: Found strictly better circuit.")
    else:
        print("WARNING: Best circuit found is not strictly better than baseline (or is same).")
else:
    print("No valid circuit found.")
