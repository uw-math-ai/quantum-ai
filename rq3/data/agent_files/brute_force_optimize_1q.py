import stim
import itertools

def get_clifford_map(circuit):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    return sim.current_inverse_tableau().inverse()

def optimize_1q(ops):
    # ops is a list of stim instructions for a single qubit
    target_circ = stim.Circuit()
    for op in ops:
        target_circ.append(op)
        
    target_tableau = get_clifford_map(target_circ)
    
    # Try 0 gates
    c = stim.Circuit()
    if get_clifford_map(c) == target_tableau:
        return c
        
    # Try 1 gate
    gates = ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"] # SQRT_Z is S
    # Actually, standard set: H, S, X, Y, Z.
    # S_DAG is S*S*S.
    # Let's restrict to H, S, X, Y, Z, S_DAG?
    # Tool volume uses: CX, CY, CZ, H, S, SQRT_X, etc.
    # So using S_DAG counts as 1 gate?
    # Yes.
    
    candidates_1 = gates
    for g in candidates_1:
        c = stim.Circuit()
        c.append(g, [0])
        if get_clifford_map(c) == target_tableau:
            return c
            
    # Try 2 gates
    for g1 in candidates_1:
        for g2 in candidates_1:
            c = stim.Circuit()
            c.append(g1, [0])
            c.append(g2, [0])
            if get_clifford_map(c) == target_tableau:
                return c
                
    # Try 3 gates (rarely needed if we have X,Y,Z)
    # The max length is 3 for H, S generators. With X,Y,Z it's usually 2.
    for g1 in candidates_1:
        for g2 in candidates_1:
            for g3 in candidates_1:
                c = stim.Circuit()
                c.append(g1, [0])
                c.append(g2, [0])
                c.append(g3, [0])
                if get_clifford_map(c) == target_tableau:
                    return c

    return target_circ # Fallback

# Parse suffix
with open("optimized_candidate.stim", "r") as f:
    full_circ = stim.Circuit(f.read())

prefix = full_circ[0:2] # H and CZ
suffix = full_circ[2:]

final_suffix = stim.Circuit()

# Group by qubit
qubit_ops = {q: [] for q in range(12)}
for op in suffix:
    for t in op.targets_copy():
        qubit_ops[t.value].append(stim.CircuitInstruction(op.name, [t.value]))

for q in range(12):
    ops = qubit_ops[q]
    if not ops:
        continue
    optimized = optimize_1q(ops)
    # Append to final_suffix, but we need to retarget to q
    for op in optimized:
        final_suffix.append(op.name, [q])

print("Optimized suffix:")
print(final_suffix)

final_circuit = prefix + final_suffix
with open("final_optimized_v2.stim", "w") as f:
    f.write(str(final_circuit))
