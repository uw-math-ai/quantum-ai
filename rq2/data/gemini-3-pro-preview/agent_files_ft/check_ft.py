import stim
import sys

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        exp = sim.peek_observable_expectation(s)
        if exp == 1:
            preserved += 1
            
    return preserved, total

def flatten_circuit(circuit):
    flat = stim.Circuit()
    for op in circuit:
        name = op.name
        targets = op.targets_copy()
        
        # Determine arity
        # simple heuristic
        if name in ["CX", "CZ", "CY", "SWAP", "ISWAP", "XCZ", "XCY", "YCX", "YCZ", "YCY"]:
            arity = 2
        elif name in ["H", "S", "X", "Y", "Z", "I", "S_DAG", "H_YZ", "H_XY", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"]:
            arity = 1
        elif name in ["M", "MX", "MY", "MZ", "MPP", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK", "QUBIT_COORDS", "SHIFT_COORDS"]:
            # These can have variable targets or don't matter for unitary analysis
            # For analysis, we can treat M as 1-qubit ops if they are single qubit measurements?
            # MPP is multi.
            # But the input only has H, S, CX.
            # And I will add H, CX, CZ, S, S_DAG, M.
            if name in ["M", "MX", "MY", "MZ"]:
                arity = 1
            else:
                # Keep as is
                flat.append(op)
                continue
        else:
            # Unknown, keep
            flat.append(op)
            continue
            
        # Split targets
        # targets is list of GateTarget
        # check if multiple args
        t_vals = [t.value for t in targets] # assuming all are qubit targets
        
        if len(t_vals) > arity:
            # Split
            for k in range(0, len(t_vals), arity):
                chunk = targets[k:k+arity]
                flat.append(name, [t.value for t in chunk]) # append takes values if standard gate
        else:
            flat.append(op)
            
    return flat

def analyze_faults(circuit, data_qubits, flag_qubits):
    # Flatten first
    circuit = flatten_circuit(circuit)
    ops = list(circuit)
    num_ops = len(ops)
    num_qubits = circuit.num_qubits
    
    suffix_tableaus = [None] * (num_ops + 1)
    current_suffix = stim.Tableau(num_qubits)
    suffix_tableaus[num_ops] = current_suffix.copy()
    
    for k in range(num_ops - 1, -1, -1):
        op = ops[k]
        try:
            name = op.name
            targets = [t.value for t in op.targets_copy() if t.is_qubit_target]
            if not targets:
                continue
            
            gate_tab = stim.Tableau.from_named_gate(name)
            # Prepend. Since we flattened, targets matches arity (or is single application).
            current_suffix.prepend(gate_tab, targets)
        except Exception:
            pass
        suffix_tableaus[k] = current_suffix.copy()

    threshold = 4
    count_A = 0
    count_B = 0
    
    pmap = {'X':1, 'Y':2, 'Z':3}
    
    for k in range(num_ops):
        op = ops[k]
        
        targets = []
        for t in op.targets_copy():
            if t.is_qubit_target:
                targets.append(t.value)
        
        if not targets:
            continue
            
        for q in targets:
            for p_char in ['X', 'Y', 'Z']:
                p_val = pmap[p_char]
                
                s_next = suffix_tableaus[k+1]
                
                ps = stim.PauliString(num_qubits)
                ps[q] = p_val
                
                propagated = s_next(ps)
                
                weight = 0
                for dq in data_qubits:
                    if propagated[dq] != 0:
                        weight += 1
                
                if weight >= threshold:
                    count_A += 1
                    
                    flagged = False
                    for fq in flag_qubits:
                        if propagated[fq] in [1, 2]:
                            flagged = True
                            break
                    
                    if not flagged:
                        count_B += 1

    score = 1.0
    if count_A > 0:
        score = 1.0 - (count_B / count_A)
        
    return score, count_A, count_B

def main():
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim", "r") as f:
            circuit_str = f.read()
        
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
            stab_lines = [l.strip() for l in f.readlines() if l.strip()]
            
        circuit = stim.Circuit(circuit_str)
        num_qubits = circuit.num_qubits
        
        data_qubits = list(range(45))
        flag_qubits = [q for q in range(num_qubits) if q > 44]
        
        print(f"Data qubits: {len(data_qubits)}")
        print(f"Flag qubits: {flag_qubits}")
        
        preserved, total_stabs = check_stabilizers(circuit, stab_lines)
        print(f"Stabilizers preserved: {preserved}/{total_stabs}")
        
        score, bad_errs, unflagged_bad = analyze_faults(circuit, data_qubits, flag_qubits)
        print(f"FT Score: {score}")
        print(f"High weight errors: {bad_errs}")
        print(f"Unflagged high weight: {unflagged_bad}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
