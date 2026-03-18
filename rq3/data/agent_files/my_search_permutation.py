import stim
import random
import time

target_stabilizers_str = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXI", "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX", "IIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXX", "ZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZI", "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ", "IIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZ", "XXXIIIIXXXIIIIXXXIIIIXXXIIIIIIIIIIIIIIIIIIIIIIIII", "XXXIIIIIIIIIIIXXXIIIIIIIIIIIXXXIIIIIIIIIIIXXXIIII", "IIIIIIIIIIIIIIXXXIIIIXXXIIIIXXXIIIIXXXIIIIIIIIIII", "ZZZIIIIZZZIIIIZZZIIIIZZZIIIIIIIIIIIIIIIIIIIIIIIII", "ZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIII", "IIIIIIIIIIIIIIZZZIIIIZZZIIIIZZZIIIIZZZIIIIIIIIIII"
]

num_qubits = 49

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name in ["CX", "CY", "CZ"]:
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "XC", "YC", "ZC"]:
             vol += len(instr.targets_copy())
    return cx, vol

def permute_stabilizers(stabs, permutation):
    new_stabs = []
    # permutation[i] is the NEW index for OLD qubit i
    # So qubit i goes to position permutation[i]
    
    for s_str in stabs:
        old_paulis = [0] * num_qubits # 0=I, 1=X, 2=Y, 3=Z
        for k in range(num_qubits):
             char = s_str[k]
             if char == 'X': old_paulis[k] = 1
             elif char == 'Y': old_paulis[k] = 2
             elif char == 'Z': old_paulis[k] = 3
        
        new_paulis = [0] * num_qubits
        for k in range(num_qubits):
            new_paulis[permutation[k]] = old_paulis[k]
        
        ns = ""
        for p in new_paulis:
            if p == 0: ns += "I"
            elif p == 1: ns += "X"
            elif p == 2: ns += "Y"
            elif p == 3: ns += "Z"
        new_stabs.append(stim.PauliString(ns))
    return new_stabs

def solve_with_perm(perm):
    # perm maps old_index -> new_index
    # Synthesize with permuted stabilizers
    pstabs = permute_stabilizers(target_stabilizers_str, perm)
    try:
        # allow_underconstrained=True because 48 stabs for 49 qubits
        tableau = stim.Tableau.from_stabilizers(pstabs, allow_underconstrained=True)
        circ = tableau.to_circuit()
        
        # Invert permutation
        inv_perm = [0]*num_qubits
        for old, new in enumerate(perm):
            inv_perm[new] = old
            
        # Remap circuit
        remapped_circ = stim.Circuit()
        for instr in circ:
            targets = instr.targets_copy()
            new_targets = []
            for t in targets:
                if t.is_qubit_target:
                    new_targets.append(inv_perm[t.value])
                else:
                    # Should not happen for standard gates from to_circuit
                    pass
            
            remapped_circ.append(instr.name, new_targets)
            
        return remapped_circ
    except Exception as e:
        return None

best_cx = 273
best_vol = 297
best_circ = None

# 1. Reverse
perm = list(range(num_qubits))
perm.reverse()
circ = solve_with_perm(perm)
if circ:
    cx, vol = get_metrics(circ)
    print(f"Reverse: CX={cx}, Vol={vol}")
    if cx < best_cx or (cx == best_cx and vol < best_vol):
        best_cx = cx
        best_vol = vol
        best_circ = circ
        print("Updated best with Reverse")

# 2. Random search
start_time = time.time()
iters = 0
while time.time() - start_time < 120: # 120 seconds
    perm = list(range(num_qubits))
    random.shuffle(perm)
    circ = solve_with_perm(perm)
    if circ:
        cx, vol = get_metrics(circ)
        if cx < best_cx or (cx == best_cx and vol < best_vol):
            print(f"Found better: CX={cx}, Vol={vol}")
            best_cx = cx
            best_vol = vol
            best_circ = circ
    iters += 1

print(f"Done {iters} iters. Best CX={best_cx}, Vol={best_vol}")

if best_circ:
    with open("best_candidate.stim", "w") as f:
        f.write(str(best_circ))
