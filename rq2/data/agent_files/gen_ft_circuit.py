import sys

def parse_stabilizers(stab_str_list):
    stabs = []
    for s in stab_str_list:
        paulis = []
        for i, char in enumerate(s):
            if char != 'I':
                paulis.append((i, char))
        stabs.append(paulis)
    return stabs

def generate_circuit():
    original_circuit = "H 0 1\nCX 0 1 0 4\nH 2 3\nCX 1 2 1 3 1 4 1 5 1 8 1 14 2 4 2 5 2 6 2 9 2 10 4 3 3 4 4 3 3 6 3 10 4 5 4 7 4 8 4 11 4 14 5 6 5 7 5 9 5 11 5 12 6 7 6 12 6 13 7 13 11 8 12 8 13 8 14 8 9 10 12 9 13 9 14 9 12 10 13 10 14 10 12 11 11 12 12 11 11 12 13 11 14 11 13 12 14 12 14 13"
    
    stabilizers = [
        "XXXXXXXXIIIIIII",
        "IXXIXXIIXXIXXII",
        "IIXXIXXIIXXXIXI",
        "IIIIXXXXIIIXXXX",
        "ZZZZIIIIIIIIIII",
        "IZZIZZIIIIIIIII",
        "IIZZIZZIIIIIIII",
        "IIIIZZZZIIIIIII",
        "IZIIZIIIZIIIZII",
        "IIZIIZIIIZIZIII",
        "IIZZIIIIIZZIIII",
        "IIIIZZIIIIIZZII",
        "IIIIIZZIIIIZIZI",
        "IIIIIIZZIIIIIZZ"
    ]
    
    parsed_stabs = parse_stabilizers(stabilizers)
    
    new_circuit_lines = [original_circuit]
    
    ancilla_start = 15
    current_ancilla = ancilla_start
    flag_qubits = []
    
    # Add gadgets
    for stab in parsed_stabs:
        # Check type
        is_z = all(p[1] == 'Z' for p in stab)
        is_x = all(p[1] == 'X' for p in stab)
        
        # Determine targets
        qubits = [p[0] for p in stab]
        
        m = current_ancilla
        f = current_ancilla + 1
        current_ancilla += 2
        
        flag_qubits.append(m)
        flag_qubits.append(f)
        
        if is_z:
            # Z-stabilizer measurement
            # m in 0. f in +.
            # CX d m. CX f m at end.
            # Measure m (Z), f (X).
            
            # Init f in + (m is 0 by default)
            new_circuit_lines.append(f"H {f}")
            
            # Apply CNOTs from data to m
            for q in qubits:
                new_circuit_lines.append(f"CX {q} {m}")
            
            # Flag check: CX f m
            new_circuit_lines.append(f"CX {f} {m}")
            
            # Measure f in X
            new_circuit_lines.append(f"H {f}")
            
            # Measure m and f
            new_circuit_lines.append(f"M {m} {f}")
            
        elif is_x:
            # X-stabilizer measurement
            # m in +. f in 0.
            # CX m d. CX m f at end.
            # Measure m (X), f (Z).
            
            # Init m in +
            new_circuit_lines.append(f"H {m}")
            
            # Apply CNOTs from m to data
            for q in qubits:
                new_circuit_lines.append(f"CX {m} {q}")
            
            # Flag check: CX m f
            new_circuit_lines.append(f"CX {m} {f}")
            
            # Measure m in X
            new_circuit_lines.append(f"H {m}")
            
            # Measure m and f (f in Z)
            new_circuit_lines.append(f"M {m} {f}")
            
    final_circuit = "\n".join(new_circuit_lines)
    
    with open("circuit.stim", "w") as f:
        f.write(final_circuit)
        
    print("FLAGS_START")
    print(flag_qubits)
    print("FLAGS_END")

if __name__ == "__main__":
    generate_circuit()
