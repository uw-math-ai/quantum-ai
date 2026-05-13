import stim

def get_stabilizers():
    return [
        "XXXIIIXXXIII",
        "IIXXXIIIXXXI",
        "XIIIXXXIIIXX",
        "XXXXXXIIIIII",
        "IIIIIIXXXXXX",
        "IIZZZZIZIZII",
        "ZIIIZIZZZIIZ",
        "ZZZIIZZIIIZI",
        "ZIIZZZIIZIZI",
        "IZZIIIZZIZIZ",
        "IZIZIIZIIIZI", # S10
        "IIZZIIZIIIIZ"  # S11
    ]

def get_base_circuit_string():
    return """CX 2 0 0 2 2 0
H 0 4
CX 0 4 0 6 0 7 0 8
H 2 3
CX 2 0 3 0 3 1 1 3 3 1
H 3
CX 1 3 1 6 1 8 1 9 1 10 2 1 2 4 2 5 2 6 2 7 2 8 2 10 2 11 3 2 3 7 3 8 3 9 3 10 5 4 4 5 5 4 4 6 4 8 7 4 9 4 10 4 11 4 7 5 5 7 7 5 5 6 10 5 7 6 6 7 7 6 6 9 6 10 6 11 8 7 7 8 8 7 7 9 8 7 11 7 9 8 8 9 9 8 8 9 10 8 11 8"""

def generate_circuit():
    base = get_base_circuit_string().replace("\n", " ")
    stabs = get_stabilizers()
    
    ancilla_start = 12
    ops = []
    ops.append(base)
    
    current_ancilla = ancilla_start
    flag_qubits = []
    
    for s in stabs:
        is_x_check = 'X' in s
        is_z_check = 'Z' in s
        
        anc = current_ancilla
        flag_qubits.append(anc)
        current_ancilla += 1
        
        # H ancilla if X check
        if is_x_check:
            ops.append(f"H {anc}")
        
        for q, char in enumerate(s):
            if char == 'X':
                # X-check: CX anc q
                ops.append(f"CX {anc} {q}")
            elif char == 'Z':
                # Z-check: CX q anc
                ops.append(f"CX {q} {anc}")
        
        # H ancilla if X check
        if is_x_check:
            ops.append(f"H {anc}")
            
        ops.append(f"M {anc}")
            
    return "\n".join(ops), flag_qubits

if __name__ == "__main__":
    c, f = generate_circuit()
    print("---CIRCUIT_START---")
    print(c)
    print("---CIRCUIT_END---")
    print("---FLAGS_START---")
    print(",".join(map(str, f)))
    print("---FLAGS_END---")
