import stim
import sys

# Define base circuit
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
    
    # Add Checks
    # 6,7 for X-check (Anc, Flag)
    # 8,9 for Z-check (Anc, Flag)
    
    # Check XXXXXX
    x_check = make_flagged_x_check([0,1,2,3,4,5], 6, 7)
    c += x_check
    
    # Check ZZZZZZ
    z_check = make_flagged_z_check([0,1,2,3,4,5], 8, 9)
    c += z_check

    # Check XXXXXX again
    x_check_2 = make_flagged_x_check([0,1,2,3,4,5], 6, 7) # Reuse ancillas? Or new ones?
    # Reusing ancillas is fine if we reset them.
    # Stim `H` resets them? No. `M` collapses them.
    # If we reuse, we need to reset to |0>.
    # M leaves them in |0> or |1>.
    # We should add "R" (reset) or use "feedback" to flip if 1.
    # Simpler: Use NEW ancillas.
    # 10, 11.
    x_check_2 = make_flagged_x_check([0,1,2,3,4,5], 10, 11)
    c += x_check_2
    
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
    
    # Ideal Stabilizers for GHZ
    ideal_stabs = ["XXXXXX", "ZZIIII", "IZZIII", "IIZZII", "IIIZZI", "IIIIZZ"]
    ideal_paulis = []
    for s_str in ideal_stabs:
        p = stim.PauliString(10)
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
    if failures == 0:
        print("SUCCESS! Circuit is FT.")
    
    # Print Circuit String
    print("FINAL CIRCUIT:")
    print(c)

if __name__ == "__main__":
    analyze_ft()
