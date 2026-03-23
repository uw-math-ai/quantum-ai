import stim
import sys

# Define the circuit and stabilizers
circuit_str = """CX 15 0 0 15 15 0
H 7
CX 7 0 11 0 16 0 5 1 1 5 5 1
H 1 2 3 4 6 15
CX 1 2 1 3 1 4 1 6 1 7 1 13 1 15 1 16 7 2 2 7 7 2 2 7 2 11 2 16 3 2 7 3 3 7 7 3 3 10 3 16 4 6 4 7 4 11 4 12 4 13 4 15 15 5 5 15 15 5
H 15
CX 5 6 5 8 5 12 5 15 7 6 6 7 7 6 6 12 6 16 10 7 7 10 10 7 7 12 11 7 15 8 8 15 15 8 8 9 8 12 8 14 10 8 10 9 9 10 10 9 9 10 9 12 9 15 10 12 10 13 11 10 12 10 13 10 14 10 16 10 14 11 11 14 14 11 11 12 11 15 13 11 15 12 12 15 15 12 13 12 15 13 13 15 15 13 14 13 16 13 16 14"""

stabilizers = [
    "IIIIIXIIIXIXXIIII", "IIIIIIIIXIXIIXIXI", "IIIXIIIXIIIIIIXIX", "IIXIIIXIIIIIIIXIX", 
    "IIIIXXXXXIXXIIIIX", "IXIIXIIIIIXIIXIII", "IIIIIIIIXXIXIIIXI", "XIXXIIIIIIIIIIXII", 
    "IIIIIZIIIZIZZIIII", "IIIIIIIIZIZIIZIZI", "IIIZIIIZIIIIIIZIZ", "IIZIIIZIIIIIIIZIZ", "IIIIZZZZZIZZIIIIZ", "IZIIZIIIIIZIIZIII", "IIIIIIIIZZIZIIIZI", "ZIZZIIIIIIIIIIZII"
]

def to_binary(ps_str):
    # ps_str like "+XIZ..."
    if ps_str.startswith('+') or ps_str.startswith('-'):
        ps_str = ps_str[1:]
    
    vec = []
    # Symplectic form: X bits then Z bits
    for c in ps_str:
        if c in ['X', 'Y']:
            vec.append(1)
        else:
            vec.append(0)
    for c in ps_str:
        if c in ['Z', 'Y']:
            vec.append(1)
        else:
            vec.append(0)
    return vec

def analyze():
    # Parse circuit
    c = stim.Circuit(circuit_str)
    
    # Flatten to single operations
    flat_ops = []
    for instr in c:
        if instr.name in ["CX", "H", "S", "X", "Y", "Z"]:
            targets = instr.targets_copy()
            if instr.name == "CX":
                for i in range(0, len(targets), 2):
                    t1 = targets[i]
                    t2 = targets[i+1]
                    if t1.is_qubit_target and t2.is_qubit_target:
                        flat_ops.append(("CX", t1.value, t2.value))
            else:
                for t in targets:
                    if t.is_qubit_target:
                        flat_ops.append((instr.name, t.value))
        else:
            pass

    print(f"Flattened ops list has {len(flat_ops)} operations.")
    
    num_qubits = 17
    
    # Parse stabilizers into PauliStrings
    stab_ps = [stim.PauliString(s) for s in stabilizers]
    
    # Prepare basis for stabilizer group
    matrix = []
    for s in stabilizers:
        matrix.append(to_binary(s))
        
    basis = []
    for row in matrix:
        r = list(row)
        for b in basis:
            pivot = -1
            for k in range(len(b)):
                if b[k]:
                    pivot = k
                    break
            
            if r[pivot]:
                for k in range(len(r)):
                    r[k] = r[k] ^ b[k]
        
        if any(r):
            basis.append(r)
            
    # Fault analysis
    bad_faults = []
    
    for i in range(len(flat_ops)):
        suffix = stim.Circuit()
        suffix.append("I", [16])
        for j in range(i+1, len(flat_ops)):
            op_j = flat_ops[j]
            if op_j[0] == "CX":
                suffix.append("CX", [op_j[1], op_j[2]])
            else:
                suffix.append(op_j[0], [op_j[1]])
        
        t = stim.Tableau.from_circuit(suffix)
        
        op = flat_ops[i]
        if op[0] == "CX":
            qubits = [op[1], op[2]]
        else:
            qubits = [op[1]]
            
        for q in qubits:
            for p_char in ["X", "Y", "Z"]:
                ps = stim.PauliString(num_qubits)
                ps[q] = p_char
                
                final_ps = t(ps)
                
                weight = sum(1 for k in range(num_qubits) if final_ps[k] != 0)
                
                if weight > 2:
                    commutes_all = True
                    for s_ps in stab_ps:
                        if not final_ps.commutes(s_ps):
                            commutes_all = False
                            break
                    
                    bad_faults.append({
                        "op_idx": i,
                        "op": op,
                        "qubit": q,
                        "error": p_char,
                        "weight": weight,
                        "commutes_all": commutes_all,
                        "final_error": str(final_ps)
                    })

    # Analyze undetectable faults
    undetectable_bad_faults = []
    logical_errors = []
    stabilizer_errors = []
    
    for f in bad_faults:
        if f['commutes_all']:
            undetectable_bad_faults.append(f)
            
            s_str = f['final_error']
            r = to_binary(s_str)
            
            # Check if r is in basis
            for b in basis:
                pivot = -1
                for k in range(len(b)):
                    if b[k]:
                        pivot = k
                        break
                if r[pivot]:
                    for k in range(len(r)):
                        r[k] = r[k] ^ b[k]
            
            if not any(r):
                stabilizer_errors.append(f)
            else:
                logical_errors.append(f)

    print(f"Total bad faults: {len(bad_faults)}")
    print(f"Undetectable bad faults (commuting with stabilizers): {len(undetectable_bad_faults)}")
    print(f"  - Stabilizer errors: {len(stabilizer_errors)}")
    print(f"  - Logical errors: {len(logical_errors)}")
    
    if len(logical_errors) > 0:
        print("CRITICAL: Found logical errors!")
        for f in logical_errors[:5]:
            print(f"Logical Error: Op {f['op_idx']} q{f['qubit']}={f['error']} -> {f['final_error']}")

if __name__ == "__main__":
    analyze()
