import stim

def generate():
    # Construct circuit string
    s = "CX 1 0 0 1 1 0\nH 0\nCX 0 2 0 3 0 8\n"
    
    anc = 9
    measurements = []
    
    def add_check_z_stab(s, anc, flag, qubits):
        # Measure Z stabilizer (Z tensor Z).
        # Ancilla (Target) |0>. Flag (Control) |+>.
        # CX Flag Anc. CX q Anc...
        s += f"H {flag}\n"
        s += f"CX {flag} {anc}\n"
        for q in qubits:
            s += f"CX {q} {anc}\n"
            s += f"CX {flag} {anc}\n"
        
        s += f"H {flag}\n"
        return s
    
    def add_check_x_stab(s, anc, flag, qubits):
        # Measure X stabilizer (X tensor X).
        # Ancilla (Control) |+>. Flag (Target) |0>.
        # CX Anc Flag. CX Anc q...
        s += f"H {anc}\n"
        s += f"CX {anc} {flag}\n"
        for q in qubits:
            s += f"CX {anc} {q}\n"
            s += f"CX {anc} {flag}\n"
        
        s += f"H {anc}\n"
        return s

    # Internal Checks (1-4)
    # 1. Z0 Z2
    s += add_check_z_stab("", anc, anc+1, [0, 2])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 2. Z0 Z3
    s += add_check_z_stab("", anc, anc+1, [0, 3])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 3. Z0 Z8
    s += add_check_z_stab("", anc, anc+1, [0, 8])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 4. X0 X2 X3 X8
    s += add_check_x_stab("", anc, anc+1, [0, 2, 3, 8])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # Continue Part 2
    s += "H 1\n"
    s += "CX 1 0 2 1 1 2 2 1 2 1 3 2 2 3 3 2 3 2 3 4 3 5 7 6 6 7 7 6 6 7 8 6 8 7\n"
    
    # Final Checks (1-9)
    # 1. Z0 Z1
    s += add_check_z_stab("", anc, anc+1, [0, 1])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 2. Z0 Z2
    s += add_check_z_stab("", anc, anc+1, [0, 2])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 3. Z3 Z4
    s += add_check_z_stab("", anc, anc+1, [3, 4])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 4. Z3 Z5
    s += add_check_z_stab("", anc, anc+1, [3, 5])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 5. Z6 Z7
    s += add_check_z_stab("", anc, anc+1, [6, 7])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 6. Z6 Z8
    s += add_check_z_stab("", anc, anc+1, [6, 8])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 7. X0..X5
    s += add_check_x_stab("", anc, anc+1, [0, 1, 2, 3, 4, 5])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 8. X0..X2 X6..X8
    s += add_check_x_stab("", anc, anc+1, [0, 1, 2, 6, 7, 8])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # 9. X0 X1 X2 (Logical Z)
    s += add_check_x_stab("", anc, anc+1, [0, 1, 2])
    measurements.extend([anc, anc+1])
    anc += 2
    
    # Final Measurements
    s += "M " + " ".join(map(str, measurements)) + "\n"
    
    return s

if __name__ == "__main__":
    print(generate())
