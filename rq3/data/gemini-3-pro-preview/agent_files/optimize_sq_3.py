import stim

def solve():
    suffix_str = """
X 12 15
Y 5 7 9 10 16
Z 4 6 8 11 13
S 1 3 4 7 14 15 16
H 0 3 5 7 8 10 11 13 14 16
S 3 8
"""
    circuit = stim.Circuit(suffix_str)
    
    # List of common single qubit gates in Stim
    gates = [
        "I", "X", "Y", "Z",
        "H", "H_XY", "H_YZ", "H_ZX",
        "S", "S_DAG",
        "SQRT_X", "SQRT_X_DAG",
        "SQRT_Y", "SQRT_Y_DAG",
        "C_XYZ", "C_ZYX", "C_XZY", "C_YXZ", "C_YZX", "C_ZXY",
    ]
    
    name_to_tableau = {}
    for g in gates:
        try:
            name_to_tableau[g] = stim.Circuit(f"{g} 0").to_tableau()
        except:
            pass

    final_ops = {}
    
    # Collect optimized ops for each qubit
    qubit_ops = {}
    
    for q in range(17):
        sub_circ = stim.Circuit()
        for op in circuit:
            targets = op.targets_copy()
            if any(t.value == q for t in targets):
                sub_circ.append(op.name, [0])
        
        target = sub_circ.to_tableau()
        
        found = None
        for name, t in name_to_tableau.items():
            if t == target:
                found = name
                break
        
        if found:
            if found != "I" and found != "C_XYZ":
                qubit_ops[q] = [found]
            else:
                qubit_ops[q] = []
        else:
            c = target.to_circuit("elimination")
            qubit_ops[q] = [op.name for op in c]

    # Output in layers
    max_len = 0
    if qubit_ops:
        max_len = max(len(ops) for ops in qubit_ops.values())
    
    for l in range(max_len):
        layer_gates = {}
        for q in range(17):
            ops = qubit_ops[q]
            if l < len(ops):
                g = ops[l]
                if g not in layer_gates: layer_gates[g] = []
                layer_gates[g].append(q)
        
        for g in sorted(layer_gates.keys()):
            print(f"{g} {' '.join(map(str, sorted(layer_gates[g])))}")

if __name__ == "__main__":
    solve()
