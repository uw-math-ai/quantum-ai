import stim
import sys

def analyze():
    # 1. Load circuit
    try:
        with open("candidate_rq2.stim", "r") as f:
            circuit_text = f.read()
    except FileNotFoundError:
        # Fallback if file not created yet, use hardcoded for first run
        circuit_text = """H 0 1 3
CX 0 1 0 3 0 6 0 8 6 1 1 6 6 1 1 5
H 2
CX 2 5 3 4 6 4 4 6 6 4 4 5 4 6 4 8 7 6 8 6 8 7
"""
    
    c = stim.Circuit(circuit_text)
    
    # 2. Define stabilizers
    stabilizers_str = [
        "XXIXXIIII", "IIIIXXIXX", "IIXIIXIII", "IIIXIIXII", 
        "IIIZZIZZI", "IZZIZZIII", "ZZIIIIIII", "IIIIIIIZZ"
    ]
    stabilizers = [stim.PauliString(s) for s in stabilizers_str]
    
    # Generate stabilizer group for weight reduction
    stab_group = {str(stim.PauliString(9))}
    for gen in stabilizers:
        current_group = list(stab_group)
        for existing in current_group:
             stab_group.add(str(stim.PauliString(existing) * gen))
    
    # 3. Flatten operations
    ops = []
    # Identify ancillas: assumed to be any qubit not in 0-8?
    # The prompt says "All ancilla qubits must be initialized...".
    # Original circuit only uses 0-8.
    # So any new qubit is ancilla.
    # We only care about errors on 0-8.
    
    for instruction in c:
        if instruction.name in ["CX", "H", "S", "X", "Y", "Z", "I", "CZ", "SWAP", "CNOT"]:
            targets = instruction.targets_copy()
            if instruction.name in ["CX", "SWAP", "CZ", "CNOT"]:
                for k in range(0, len(targets), 2):
                    ops.append((instruction.name, [targets[k].value, targets[k+1].value]))
            else:
                for t in targets:
                    ops.append((instruction.name, [t.value]))
        elif instruction.name == "M":
             # Measurement is a location too, but usually at end.
             pass

    # 4. Propagate faults
    # We want to find: Location index -> List of bad faults
    
    bad_locations = {}
    
    # Build full tableau T_total to check if circuit works (preserves stabilizers)
    # T_total maps Input -> Output.
    # But for state prep, Input is |0>. Output should be stabilized.
    # Check: For each S in stabilizers, S |psi> = |psi>.
    # Equivalent to: T_total^-1(S) should be Z-type on input qubits initialized to 0?
    # Or simpler: Stim's TableauSimulator can check.
    
    sim_check = stim.TableauSimulator()
    sim_check.do(c)
    # Check stabilizers
    for s in stabilizers:
        if sim_check.peek_observable_expectation(s) != 1:
            print(f"WARNING: Stabilizer {s} not preserved by circuit!")
    
    # Propagation for Faults
    # We'll re-use the suffix tableau strategy.
    
    t_suffix = [None] * (len(ops) + 1)
    t_curr = stim.Tableau(stim.Circuit(circuit_text).num_qubits)
    # Note: num_qubits might increase if we add ancillas. 
    # Use explicit size if needed, or rely on Stim.
    
    t_suffix[len(ops)] = t_curr.copy()
    
    for i in range(len(ops) - 1, -1, -1):
        op_name, targets = ops[i]
        mini = stim.Circuit()
        for k in range(9): mini.append("I", [k])
        mini.append(op_name, targets)
        t_op = stim.Tableau.from_circuit(mini)
        t_suffix[i] = t_op.then(t_suffix[i+1])
        
    print(f"Analyzed {len(ops)} operations.")

    bad_count = 0
    for i in range(len(ops) + 1):
        t = t_suffix[i]
        
        # Check X and Z faults on all data qubits 0-8
        for q in range(9):
            for p_type in ["X", "Z"]:
                ps = stim.PauliString(len(t)) # size
                if p_type == "X": ps[q] = 1
                elif p_type == "Z": ps[q] = 2
                
                e_final = t(ps)
                
                # Check weight on data qubits 0-8 only
                # We need to mask e_final to 0-8?
                # Actually, the error is defined on the whole system, but we only care about data errors?
                # "propagates to less than floor((3 - 1)/ 2) data qubits"
                # So we count weight on 0-8.
                
                # We need to reduce E_final by stabilizers to find min weight.
                
                # Project E_final to 0-8
                # But stabilizers are on 0-8.
                # So just take the 0-8 part.
                
                e_data = stim.PauliString(9)
                for k in range(9):
                    e_data[k] = e_final[k]
                
                # Find min weight
                min_w = 999
                for s_str in stab_group:
                    s = stim.PauliString(s_str)
                    combined = e_data * s
                    w = combined.weight
                    if w < min_w:
                        min_w = w
                
                if min_w > 1:
                    # In original circuit, no flags. So this is bad.
                    if i < len(ops):
                        op_desc = f"{ops[i][0]} {ops[i][1]}"
                    else:
                        op_desc = "END"
                    
                    if i not in bad_locations: bad_locations[i] = []
                    bad_locations[i].append(f"Q{q}{p_type}")
                    bad_count += 1
    
    print(f"Found {bad_count} unflagged high-weight faults.")
    
    # Print summary of bad locations
    for i in sorted(bad_locations.keys()):
        op = ops[i] if i < len(ops) else "END"
        faults = bad_locations[i]
        # Summarize
        print(f"Loc {i}: {op} -> {len(faults)} faults (e.g. {faults[:3]})")

if __name__ == "__main__":
    analyze()
