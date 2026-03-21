
def generate_circuit():
    circuit = []
    
    # Block 1: SWAP
    circuit.append("CX 2 0 0 2 2 0")
    
    # Check 0 and 2 (expect |0>)
    # Detects X errors.
    # Use ancillas 7, 8
    circuit.append("CX 0 7 2 8")
    circuit.append("M 7 8")
    
    # Block 2: H
    circuit.append("H 0 1 2")
    
    # Check 0, 1, 2 (expect |+>)
    # Detects Z errors.
    # Use ancillas 9, 10, 11
    circuit.append("H 9 10 11")
    circuit.append("CX 9 0 10 1 11 2")
    circuit.append("H 9 10 11")
    circuit.append("M 9 10 11")
    
    # Block 3: Rest
    circuit.append("CX 0 1 0 2 0 5 1 4 1 5 1 6 2 3 2 5 2 6 4 3 3 4 4 3 5 3 6 3 5 4 6 4")
    
    # Block 4: Final Stabilizer Checks
    # Use ancillas 12, 13, 14, 15, 16, 17
    
    # X Stabilizers (Measure X, detect Z)
    # Stab 0: IIXIXXX (2,4,5,6)
    circuit.append("H 12")
    circuit.append("CX 12 2 12 4 12 5 12 6")
    circuit.append("H 12")
    
    # Stab 1: IXIXIXX (1,3,5,6)
    circuit.append("H 13")
    circuit.append("CX 13 1 13 3 13 5 13 6")
    circuit.append("H 13")
    
    # Stab 2: XXXIIXI (0,1,2,5)
    circuit.append("H 14")
    circuit.append("CX 14 0 14 1 14 2 14 5")
    circuit.append("H 14")
    
    # Z Stabilizers (Measure Z, detect X)
    # Stab 3: IIZIZZZ (2,4,5,6)
    circuit.append("CX 2 15 4 15 5 15 6 15")
    
    # Stab 4: IZIZIZZ (1,3,5,6)
    circuit.append("CX 1 16 3 16 5 16 6 16")
    
    # Stab 5: ZZZIIZI (0,1,2,5)
    circuit.append("CX 0 17 1 17 2 17 5 17")
    
    # Measure all check ancillas
    circuit.append("M 12 13 14 15 16 17")
    
    return "\n".join(circuit)

if __name__ == "__main__":
    print(generate_circuit())
