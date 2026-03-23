import stim
import sys
from typing import List, Tuple, Set

def get_original_circuit_text() -> str:
    return """
CX 1 0 0 1 1 0
H 0
CX 0 2 0 3 0 8
H 1
CX 1 0 2 1 1 2 2 1 2 1 3 2 2 3 3 2 3 2 3 4 3 5 7 6 6 7 7 6 6 7 8 6 8 7
"""

def get_original_circuit() -> stim.Circuit:
    return stim.Circuit(get_original_circuit_text())

def get_stabilizers() -> List[stim.PauliString]:
    stabs = [
        "XXXXXXIII", "XXXIIIXXX", 
        "ZZIIIIIII", "ZIZIIIIII", 
        "IIIZZIIII", "IIIZIZIII", 
        "IIIIIIZZI", "IIIIIIZIZ"
    ]
    return [stim.PauliString(s) for s in stabs]

def get_all_stabilizers_group(generators: List[stim.PauliString]) -> List[stim.PauliString]:
    group = {str(stim.PauliString("I"*9))}
    for gen in generators:
        new_elements = set()
        for existing in group:
            existing_ps = stim.PauliString(existing)
            new_elements.add(str(existing_ps * gen))
        group.update(new_elements)
    return [stim.PauliString(s) for s in group]

def get_error_weight(error: stim.PauliString, stabilizer_group: List[stim.PauliString]) -> int:
    min_w = 999
    base_w = sum(1 for k in range(9) if error[k] != 0)
    if base_w <= 1:
        return base_w
    for s in stabilizer_group:
        combined = error * s
        w = sum(1 for k in range(9) if combined[k] != 0)
        if w < min_w:
            min_w = w
    return min_w

def decompose_circuit(c: stim.Circuit) -> List[Tuple[str, List[int]]]:
    ops = []
    for op in c:
        if op.name in ["CX", "H", "S", "X", "Y", "Z", "I", "SWAP", "CZ"]:
            targets = op.targets_copy()
            arity = 2 if op.name in ["CX", "SWAP", "CZ"] else 1
            if arity == 2:
                for k in range(0, len(targets), 2):
                    ops.append((op.name, [t.value for t in targets[k:k+2]]))
            else:
                for t in targets:
                    ops.append((op.name, [t.value for t in targets]))
        elif op.name in ["M", "R", "MR"]:
             targets = op.targets_copy()
             for t in targets:
                 ops.append((op.name, [t.value]))
    return ops

def evaluate(candidate_text: str):
    try:
        candidate = stim.Circuit(candidate_text)
    except Exception as e:
        print(f"Error parsing circuit: {e}")
        return

    sim = stim.TableauSimulator()
    sim.do(candidate)
    
    generators = get_stabilizers()
    for g in generators:
        if sim.peek_observable_expectation(g) != 1:
            print(f"STABILIZER FAIL: {g} not preserved")
            return

    print("Stabilizers preserved.")

    orig_ops = decompose_circuit(get_original_circuit())
    cand_ops = decompose_circuit(candidate)
    
    mapping = [] 
    cand_idx = 0
    for o_op in orig_ops:
        found = False
        while cand_idx < len(cand_ops):
            c_op = cand_ops[cand_idx]
            if c_op[0] == o_op[0] and c_op[1] == o_op[1]:
                mapping.append(cand_idx)
                found = True
                cand_idx += 1
                break
            cand_idx += 1
        if not found:
            print(f"MAPPING FAIL: Could not find original op {o_op} in candidate.")
            return

    print(f"Mapped {len(mapping)} original operations.")
    
    stabilizer_group = get_all_stabilizers_group(generators)
    
    # Use full state stabilizer group (including logical operators)
    # This ensures that logical operators (which stabilize the specific state) are counted as weight 0.
    sim_ideal = stim.TableauSimulator()
    sim_ideal.do(candidate)
    state_stabs = sim_ideal.canonical_stabilizers()
    stabilizer_group = get_all_stabilizers_group(state_stabs)

    ideal_meas = sim_ideal.current_measurement_record()
    
    faults_gt_1 = 0
    faults_unflagged_gt_1 = 0
    
    print("Simulating faults...")
    
    flat_candidate = cand_ops 
    
    for k, cand_flat_idx in enumerate(mapping):
        target_qubits = flat_candidate[cand_flat_idx][1]
        
        for q in target_qubits:
            for p_type in ["X", "Y", "Z"]:
                
                sim_fault = stim.TableauSimulator()
                
                for i in range(cand_flat_idx + 1):
                    op, targs = flat_candidate[i]
                    sim_fault.do(stim.Circuit(f"{op} " + " ".join(map(str, targs))))
                    
                sim_fault.do(stim.Circuit(f"{p_type} {q}"))
                
                for i in range(cand_flat_idx + 1, len(flat_candidate)):
                    op, targs = flat_candidate[i]
                    sim_fault.do(stim.Circuit(f"{op} " + " ".join(map(str, targs))))
                    
                fault_meas = sim_fault.current_measurement_record()
                
                if len(fault_meas) != len(ideal_meas):
                     print("Error: Meas count mismatch")
                     return
                     
                flagged = False
                for m_i, m_val in enumerate(fault_meas):
                    if m_val != ideal_meas[m_i]:
                        flagged = True
                        break
                
                suffix_unitary = stim.Circuit()
                # Ensure correct number of qubits by adding identity on max qubit
                suffix_unitary.append("I", [sim_fault.num_qubits - 1])
                for i in range(cand_flat_idx + 1, len(flat_candidate)):
                    op, targs = flat_candidate[i]
                    if op not in ["M", "R", "MR"]:
                        suffix_unitary.append(op, targs)
                        
                t_suffix = stim.Tableau.from_circuit(suffix_unitary)
                p_stim = stim.PauliString(sim_fault.num_qubits)
                if p_type == "X": p_stim[q] = 1
                elif p_type == "Z": p_stim[q] = 2
                elif p_type == "Y": p_stim[q] = 3
                
                p_out = t_suffix(p_stim)
                
                p_data_str = ""
                for qi in range(9):
                    val = p_out[qi]
                    if val == 0: p_data_str += "I"
                    elif val == 1: p_data_str += "X"
                    elif val == 2: p_data_str += "Z"
                    elif val == 3: p_data_str += "Y"
                
                w = get_error_weight(stim.PauliString(p_data_str), stabilizer_group)
                
                if w > 1:
                    faults_gt_1 += 1
                    if not flagged:
                        faults_unflagged_gt_1 += 1
                        print(f"UNFLAGGED: {p_type} at op {k} (q{q}) -> Weight {w}")

    if faults_gt_1 == 0:
        ft_score = 1.0
    else:
        ft_score = 1.0 - (faults_unflagged_gt_1 / faults_gt_1)
        
    print(f"Total faults > 1: {faults_gt_1}")
    print(f"Unflagged > 1: {faults_unflagged_gt_1}")
    print(f"FT Score: {ft_score}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            evaluate(f.read())
    else:
        evaluate(get_original_circuit_text())
