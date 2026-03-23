import stim
import sys

def get_circuit_text():
    return """
CX 2 0 0 2 2 0
H 0 4
CX 0 3 0 4
H 2
CX 2 0 3 1 1 3 3 1
H 1 2 4
CX 1 2 1 4
H 3
CX 3 1
H 3
CX 2 3
H 4
CX 4 2 4 3 3 4 4 3
H 3
CX 3 4
H 4
CX 4 3
H 2
S 2 2
H 2
S 0 0 2 2
"""

def analyze_faults():
    circuit = stim.Circuit(get_circuit_text())
    
    ops = []
    for instr in circuit:
        if instr.name in ["CX", "H", "S", "X", "Y", "Z", "I", "SWAP", "CZ"]:
            targets = instr.targets_copy()
            arity = 2 if instr.name in ["CX", "SWAP", "CZ"] else 1
            if arity == 2:
                for k in range(0, len(targets), 2):
                    ops.append((instr.name, [t.value for t in targets[k:k+2]]))
            else:
                for t in targets:
                    ops.append((instr.name, [t.value]))
            
    print(f"Total operations: {len(ops)}")
    
    suffix_tableaus = []
    for i in range(len(ops) + 1):
        c = stim.Circuit()
        c.append("I", [0, 1, 2, 3, 4]) # Ensure 5 qubits
        for j in range(i, len(ops)):
            op_name, targs = ops[j]
            c.append(op_name, targs)
        suffix_tableaus.append(stim.Tableau.from_circuit(c).inverse())

    # Get FULL stabilizer group of output
    sim_full = stim.TableauSimulator()
    sim_full.do(circuit)
    final_tableau = sim_full.current_inverse_tableau().inverse()
    full_stabilizers = []
    print("Full stabilizer group generators:")
    for k in range(5):
        stab = final_tableau.z_output(k)
        full_stabilizers.append(stab)
        print(f"  {stab}")

    bad_faults = []
    
    # Check all locations and all qubits
    for i in range(len(ops) + 1):
        for q in range(5):
            for p_char in ["X", "Y", "Z"]:
                p = stim.PauliString(5)
                if p_char == "X": p[q] = 1
                elif p_char == "Z": p[q] = 2
                elif p_char == "Y": p[q] = 3
                
                error = suffix_tableaus[i](p)
                w = sum(1 for k in range(5) if error[k] != 0)
                
                if w > 1: # Only care about weight > 1 (fault tolerance condition)
                    # Check detectability against FULL group
                    detectors = []
                    for idx, stab in enumerate(full_stabilizers):
                        if not error.commutes(stab):
                            detectors.append(idx)
                    
                    if not detectors:
                        # Commutes with all 5 generators -> Must be trivial (or global phase)
                        pass
                    else:
                        bad_faults.append({
                            "location": i,
                            "fault": f"{p_char}_{q}",
                            "error": str(error),
                            "weight": w,
                            "detectors": detectors
                        })

    print(f"Found {len(bad_faults)} detectable weight > 1 errors.")
    
    # Recommend stabilizers
    universe = set(range(len(bad_faults)))
    covered = set()
    chosen_indices = []
    
    while len(covered) < len(universe):
        best_stab = -1
        best_cnt = -1
        
        for stab_idx in range(len(full_stabilizers)):
            if stab_idx in chosen_indices: continue
            
            cnt = 0
            for k in universe:
                if k not in covered:
                    if stab_idx in bad_faults[k]["detectors"]:
                        cnt += 1
            
            if cnt > best_cnt:
                best_cnt = cnt
                best_stab = stab_idx
        
        if best_cnt <= 0:
            print("Cannot cover all faults!")
            break
            
        chosen_indices.append(best_stab)
        for k in universe:
            if best_stab in bad_faults[k]["detectors"]:
                covered.add(k)
                
    print("Recommended stabilizers to measure:")
    for idx in chosen_indices:
        print(f"  {full_stabilizers[idx]}")

if __name__ == "__main__":
    analyze_faults()
