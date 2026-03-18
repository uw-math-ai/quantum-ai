
def get_original_lines():
    raw = """CX 2 0 0 2 2 0
H 0 4
CX 0 3 0 4
H 2
CX 2 0 3 1 1 3 3 1
H 1 2 4
CX 1 2 1 4
H 3
CX 3 1
H 3
CX 2 3
H 4
CX 4 2 4 3 3 4 4 3
H 3
CX 3 4
H 4
CX 4 3
H 2
S 2 2
H 2
S 0 0 2 2"""
    return raw.split('\n')

def generate_circuit():
    lines = get_original_lines()
    
    # Insert checks after first line (SWAP 2 0)
    # Check Z0 and Z2 using ancillas 9, 10
    # Init 9, 10
    
    new_lines = []
    # Add init for 9, 10? (Implicitly 0)
    # We can't put init in middle easily in Stim without reset.
    # But new qubits are 0.
    
    # Process line 0
    new_lines.append(lines[0]) # CX 2 0 0 2 2 0
    
    # Add checks
    new_lines.append("CX 0 9")
    new_lines.append("CX 2 10")
    
    # Rest of circuit
    new_lines.extend(lines[1:])
    
    # Stabilizer measurements at end (5,6,7,8)
    stabs = []
    stabs.append("H 5 6 7 8")
    
    # S1: XZZXI (0,1,2,3) -> 5
    stabs.append("CX 5 0")
    stabs.append("CZ 5 1")
    stabs.append("CZ 5 2")
    stabs.append("CX 5 3")
    
    # S2: IXZZX (1,2,3,4) -> 6
    stabs.append("CX 6 1")
    stabs.append("CZ 6 2")
    stabs.append("CZ 6 3")
    stabs.append("CX 6 4")
    
    # S3: XIXZZ (0,2,3,4) -> 7
    stabs.append("CX 7 0")
    stabs.append("CX 7 2")
    stabs.append("CZ 7 3")
    stabs.append("CZ 7 4")
    
    # S4: ZXIXZ (0,1,3,4) -> 8
    stabs.append("CZ 8 0")
    stabs.append("CX 8 1")
    stabs.append("CX 8 3")
    stabs.append("CZ 8 4")
    
    stabs.append("H 5 6 7 8")
    stabs.append("M 5 6 7 8 9 10")
    
    return "\n".join(new_lines + stabs)

print(generate_circuit())
