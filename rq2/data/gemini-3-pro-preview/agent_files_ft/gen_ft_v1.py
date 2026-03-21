import stim

def generate_ft_circuit(input_circuit_str):
    # Parse input circuit
    # The input format is slightly loose, with multiple args for CX and H
    # We normalize it to a list of atomic operations
    
    lines = input_circuit_str.strip().split('\n')
    ops = []
    
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        gate = parts[0]
        args = [int(x) for x in parts[1:]]
        
        if gate == 'H':
            for q in args:
                ops.append(('H', [q]))
        elif gate == 'CX':
            # CX c1 t1 c2 t2 ...
            if len(args) % 2 != 0:
                raise ValueError(f"Invalid CX args: {args}")
            for i in range(0, len(args), 2):
                ops.append(('CX', [args[i], args[i+1]]))
        else:
            # Assume single qubit gates or valid stim lines
            # For this problem we only see H and CX
            pass

    # Reconstruction with flags
    new_circuit = []
    
    # State tracking
    # active_checks[q] = {'type': 'C'|'T', 'flag': flag_qubit_index}
    active_checks = {}
    
    next_flag = 28 # Start after data qubits (0-27)
    flag_qubits = []
    
    def close_check(q):
        if q not in active_checks:
            return
        info = active_checks[q]
        f = info['flag']
        ctype = info['type']
        
        # Add closing operations
        if ctype == 'C':
            # X-check: CX q f
            new_circuit.append(f"CX {q} {f}")
        elif ctype == 'T':
            # Z-check: CX f q, H f
            new_circuit.append(f"CX {f} {q}")
            new_circuit.append(f"H {f}")
            
        del active_checks[q]

    def start_check(q, ctype):
        nonlocal next_flag
        f = next_flag
        next_flag += 1
        flag_qubits.append(f)
        
        active_checks[q] = {'type': ctype, 'flag': f}
        
        # Add opening operations
        if ctype == 'C':
            # X-check: CX q f (f is 0)
            new_circuit.append(f"CX {q} {f}")
        elif ctype == 'T':
            # Z-check: H f, CX f q
            new_circuit.append(f"H {f}")
            new_circuit.append(f"CX {f} {q}")

    for op in ops:
        gate, targets = op
        
        if gate == 'H':
            q = targets[0]
            # Close any active check on q
            close_check(q)
            # Emit H
            new_circuit.append(f"H {q}")
            
        elif gate == 'CX':
            c, t = targets
            
            # Manage Control q (c)
            if c in active_checks:
                if active_checks[c]['type'] != 'C':
                    close_check(c)
                    start_check(c, 'C')
                # else: extend existing C-block
            else:
                start_check(c, 'C')
                
            # Manage Target q (t)
            if t in active_checks:
                if active_checks[t]['type'] != 'T':
                    close_check(t)
                    start_check(t, 'T')
                # else: extend existing T-block
            else:
                start_check(t, 'T')
            
            # Emit CX
            new_circuit.append(f"CX {c} {t}")

    # Close all remaining checks
    for q in list(active_checks.keys()):
        close_check(q)

    # Format output
    # Just join with newlines
    return "\n".join(new_circuit), flag_qubits

# Input circuit
circuit_text = """CX 24 0 0 24 24 0
H 0 2 3 5 10 11
CX 0 2 0 3 0 5 0 10 0 11 0 20 0 25 0 26 0 27
H 8
CX 8 0 20 1 1 20 20 1 1 16 1 25
H 4
CX 4 1 8 1 8 2 2 8 8 2 2 4 2 12 2 25
H 24
CX 24 2 16 3 3 16 16 3 3 25 4 3 12 3 24 4 4 24 24 4 4 24 24 5 5 24 24 5 5 12 5 25 12 6 6 12 12 6 6 25 25 7 7 25 25 7 7 21
H 9
CX 9 7 18 7 19 7 22 7 23 7 26 7 27 7 9 8 8 9 9 8
H 20
CX 8 17 8 20 24 8 20 9 9 20 20 9 9 13 9 21 24 10 10 24 24 10 10 21 13 11 11 13 13 11 17 11 21 12 12 21 21 12 12 17 18 12 19 12 22 12 23 12 26 12 27 12 17 13 13 17 17 13 18 13 19 13 22 13 23 13 26 13 27 13 24 14 14 24 24 14
H 21
CX 14 20 14 21 14 22 21 15 15 21 21 15 15 18 15 22 15 26 20 16 16 20 20 16 16 22 16 24 16 26 18 17 17 18 18 17 22 17 26 17 24 18 18 24 24 18 22 18 26 18 22 19 19 22 22 19 26 20 20 26 26 20 24 21 21 24 24 21
H 25
CX 21 23 21 25 21 26 25 22 22 25 25 22 22 23 22 25 22 27 26 23 23 26 26 23 23 24 23 26 23 27 25 24 24 25 25 24 26 24 27 24 26 25 27 25"""

ft_circuit, flags = generate_ft_circuit(circuit_text)

# We need to output the circuit and flags for the tool call
# We'll print a separator to parse easily
print("---CIRCUIT---")
print(ft_circuit)
print("---FLAGS---")
print(flags)
