import stim
import sys

base_stim = """
H 0
CX 0 1 0 2 0 3 0 4 0 5
CX 2 1 3 1 4 1 5 1
"""

def get_base_circuit():
    return stim.Circuit(base_stim)

def make_flagged_x_check(data_qubits, ancilla_idx, flag_idx, reverse=False):
    # Measures X parity.
    c = stim.Circuit()
    c.append("H", [ancilla_idx]) 
    c.append("CX", [ancilla_idx, flag_idx]) 
    qs = data_qubits[::-1] if reverse else data_qubits
    for q in qs:
        c.append("CX", [ancilla_idx, q])
    c.append("CX", [ancilla_idx, flag_idx]) 
    c.append("H", [ancilla_idx])
    c.append("M", [ancilla_idx, flag_idx])
    return c

def make_flagged_z_check(data_qubits, ancilla_idx, flag_idx):
    # Measures Z parity.
    c = stim.Circuit()
    c.append("H", [flag_idx])
    c.append("CX", [flag_idx, ancilla_idx]) 
    for q in data_qubits:
        c.append("CX", [q, ancilla_idx])
    c.append("CX", [flag_idx, ancilla_idx]) 
    c.append("H", [flag_idx])
    c.append("M", [ancilla_idx, flag_idx])
    return c

def analyze_ft():
    c = get_base_circuit()
    
    # Check XXXXXX
    c += make_flagged_x_check([0,1,2,3,4,5], 6, 7)
    
    # Check ZZZZZZ
    c += make_flagged_z_check([0,1,2,3,4,5], 8, 9)

    # Check XXXXXX again (reversed)
    c += make_flagged_x_check([0,1,2,3,4,5], 10, 11, reverse=True)
    
    ops = []
    for instr in c:
        if instr.name in ["CX", "H", "S", "X", "Y", "Z", "I", "SWAP", "CZ", "CY", "M"]:
             targets = instr.targets_copy()
             arity = 2 if instr.name in ["CX", "SWAP", "CZ", "CY"] else 1
             if instr.name == "M":
                 for t in targets: ops.append((instr.name, [t.value]))
             elif arity == 2:
                 for k in range(0, len(targets), 2):
                     ops.append((instr.name, [t.value for t in targets[k:k+2]]))
             else:
                 for t in targets: ops.append((instr.name, [t.value]))
    
    qubits = [0,1,2,3,4,5,6,7,8,9,10,11]
    failures = 0
    total = 0
    
    ideal_stabs = ["XXXXXX", "Z0Z1", "Z1Z2", "Z2Z3", "Z3Z4", "Z4Z5"]
    ideal_paulis = []
    for s_str in ideal_stabs:
        p = stim.PauliString(12) # Size 12
        # Parse Z0Z1 format
        if "Z" in s_str and "X" not in s_str and len(s_str) < 6:
             # Z0Z1 etc.
             # Assume format is pairs.
             # Extract indices?
             # My list was explicit strings before.
             pass
    
    # Let's just hardcode the strings corresponding to Z0Z1 etc.
    # Z0Z1 -> ZZIIII
    # Z1Z2 -> IZZIII
    # Z2Z3 -> IIZZII
    # Z3Z4 -> IIIZZI
    # Z4Z5 -> IIIIZZ
    
    stab_strings = ["XXXXXX", "ZZIIII", "IZZIII", "IIZZII", "IIIZZI", "IIIIZZ"]
    
    for s_str in stab_strings:
        p = stim.PauliString(12)
        for k, char in enumerate(s_str):
             if char == 'X': p[k] = 1
             elif char == 'Z': p[k] = 2
        ideal_paulis.append(p)

        
    print(f"Total ops: {len(ops)}")
    
    for i in range(len(ops) + 1):
        for q in qubits:
            for p in ["X", "Y", "Z"]:
                total += 1
                sim = stim.TableauSimulator()
                
                # Pre-fault
                for k in range(i):
                    op, targs = ops[k]
                    sim.do(stim.Circuit(f"{op} " + " ".join(map(str, targs))))
                
                # Fault
                if p == "X": sim.x(q)
                elif p == "Y": sim.y(q)
                elif p == "Z": sim.z(q)
                
                # Post-fault
                for k in range(i, len(ops)):
                    op, targs = ops[k]
                    sim.do(stim.Circuit(f"{op} " + " ".join(map(str, targs))))
                
                # Check results
                meas = sim.current_measurement_record()
                flagged = False
                for m in meas:
                    if m: flagged = True
                
                if flagged:
                    continue
                
                # Check data errors
                error_on_data = False
                for ps in ideal_paulis:
                    if sim.peek_observable_expectation(ps) == -1:
                        error_on_data = True
                        break
                
                if error_on_data:
                    failures += 1
                    if failures <= 5:
                         print(f"FAIL at op_idx={i} q={q} p={p}")

    print(f"Failures: {failures} / {total}")
    print("FINAL CIRCUIT:")
    print(c)

if __name__ == "__main__":
    analyze_ft()
