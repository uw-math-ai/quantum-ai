import stim
import itertools

def solve():
    # The tail operations on each qubit
    # We parse the manual lists
    # X 2
    # Z 0 4 6 8 10 12 14
    # S 3 4 5 6 11 12 13 14
    # H 0 3 4 5 6 8 9 10 11 12 13 14
    # S 3
    
    # Operations per qubit
    ops = {i: [] for i in range(15)}
    
    # Add gates in order
    ops[2].append('X')
    
    for i in [0, 4, 6, 8, 10, 12, 14]:
        ops[i].append('Z')
        
    for i in [3, 4, 5, 6, 11, 12, 13, 14]:
        ops[i].append('S')
        
    for i in [0, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14]:
        ops[i].append('H')
        
    ops[3].append('S')
    
    # Optimize each qubit
    new_ops = {i: [] for i in range(15)}
    
    # Available gates for optimization
    # We want to minimize volume (count of gates)
    # Gates: I, X, Y, Z, H, S, S_DAG, SQRT_X, SQRT_X_DAG, SQRT_Y, SQRT_Y_DAG
    # We can perform BFS to find shortest equivalent sequence
    
    gate_set = ["I", "X", "Y", "Z", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "C_XYZ", "C_ZYX"]
    # C_XYZ etc are single qubit cliffords but Stim might not use them as primitives for volume?
    # Volume counts: CX, CY, CZ, H, S, S_DAG, SQRT_X, SQRT_X_DAG, SQRT_Y, SQRT_Y_DAG.
    # X, Y, Z are composed?
    # Usually X = H S S H? No X is Pauli.
    # Wait, volume usually counts 1-qubit gates as 1?
    # If the metric is just "total gate count", then X is 1 gate.
    
    # Let's assume all listed in gate_set are cost 1.
    # Except "I" is cost 0.
    
    for q in range(15):
        if not ops[q]:
            continue
            
        # Build target tableau
        circuit = stim.Circuit()
        for g in ops[q]:
            circuit.append(g, [0])
        target_tableau = stim.Tableau.from_circuit(circuit)
        
        # BFS for shortest equivalent
        found = False
        for length in range(4): # 0, 1, 2, 3
            if found: break
            for cand_gates in itertools.product(gate_set, repeat=length):
                cand_circ = stim.Circuit()
                for g in cand_gates:
                    if g != "I":
                        cand_circ.append(g, [0])
                
                if stim.Tableau.from_circuit(cand_circ) == target_tableau:
                    # Found it!
                    if length == 0:
                        print(f"Qubit {q}: Identity (was {ops[q]})")
                    else:
                        print(f"Qubit {q}: {cand_gates} (was {ops[q]})")
                        for g in cand_gates:
                            if g != "I":
                                new_ops[q].append(g)
                    found = True
                    break
        
        if not found:
            print(f"Qubit {q}: Could not optimize (kept {ops[q]})")
            new_ops[q] = ops[q]

    # Reconstruct the tail lines
    # We can group by gate type to make it look nice, or just list per qubit
    # To keep file size small, we can group.
    
    print("\n--- Optimized Tail ---")
    
    # Collect by gate
    gates_map = {} # gate -> list of qubits
    for q in range(15):
        for g in new_ops[q]:
            if g not in gates_map:
                gates_map[g] = []
            gates_map[g].append(q)
            
    # Need to output in a valid order?
    # No, single qubit gates on different qubits commute.
    # BUT multiple gates on SAME qubit must be ordered.
    # My BFS returns a sequence. I need to schedule them.
    # Simple way: Layer 1, Layer 2, Layer 3.
    
    max_len = max(len(new_ops[q]) for q in range(15))
    for l in range(max_len):
        layer_gates = {}
        for q in range(15):
            if l < len(new_ops[q]):
                g = new_ops[q][l]
                if g not in layer_gates:
                    layer_gates[g] = []
                layer_gates[g].append(q)
        
        for g, qs in layer_gates.items():
            qs.sort()
            print(f"{g} " + " ".join(map(str, qs)))

if __name__ == "__main__":
    solve()
