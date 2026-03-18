import stim

stabilizers_str = """
XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI
IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX
XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ
ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
"""

stabilizers = [stim.PauliString(line.strip()) for line in stabilizers_str.splitlines() if line.strip()]

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    for instruction in circuit:
        if instruction.name == "CX":
            n = len(instruction.targets_copy()) // 2
            cx_count += n
            volume += n
        elif instruction.name == "CZ":
            n = len(instruction.targets_copy()) // 2
            # Decompose CZ into H CX H
            # CX = 1 CX, 1 Volume (in our metric?)
            # Wait, volume rule: 
            # volume = total gate count in volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)
            # So CZ counts as 1 gate in volume if allowed?
            # The prompt says: "volume - total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
            # BUT the optimization rule says: "cx_count - number of CX (CNOT) gates".
            # If I use CZ, I need to convert it to CX for the cx_count metric.
            # CZ(a,b) = H(b) CX(a,b) H(b)
            # So 1 CZ = 1 CX + 2 H.
            cx_count += n
            volume += n # CZ itself is a volume gate? Yes.
            # But if I convert to CX, volume increases.
            # The prompt implies we should submit a circuit with CX, not CZ, if we want to minimize CX count.
            # If I submit CZ, does evaluate_optimization convert it?
            # Usually stim circuits are composed of clifford gates.
            # Let's assume we need to convert CZ to CX+H to be safe and accurate on CX count.
        elif instruction.name in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "XCZ", "YCX"]:
             volume += len(instruction.targets_copy())
    return cx_count, volume

# Try elimination
try:
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circ_elim = tableau.to_circuit("elimination")
    cx, vol = count_metrics(circ_elim)
    print(f"Elimination: CX={cx}, Volume={vol}")
    with open("candidate_elimination.stim", "w") as f:
        f.write(str(circ_elim))
except Exception as e:
    print(f"Elimination failed: {e}")

# Try graph state
try:
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circ_graph = tableau.to_circuit("graph_state")
    
    # Convert CZ to CX + H
    # Strategy: iterate and replace
    new_circ = stim.Circuit()
    for inst in circ_graph:
        if inst.name == "CZ":
            targets = inst.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i]
                t = targets[i+1]
                new_circ.append("H", [t])
                new_circ.append("CX", [c, t])
                new_circ.append("H", [t])
        else:
            new_circ.append(inst)
            
    cx, vol = count_metrics(new_circ)
    print(f"Graph State (converted): CX={cx}, Volume={vol}")
    with open("candidate_graph.stim", "w") as f:
        f.write(str(new_circ))
except Exception as e:
    print(f"Graph State failed: {e}")

