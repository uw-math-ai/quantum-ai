
def get_circuit():
    # Original circuit
    c = []
    c.append("H 0 1 3")
    c.append("CX 0 1 0 3 0 6 0 8 6 1 1 6 6 1 1 5")
    c.append("H 2")
    c.append("CX 2 5 3 4 6 4 4 6 6 4 4 5 4 6 4 8 7 6 8 6 8 7")
    
    # Stabilizer Measurements
    # X stabilizers: 9, 10, 11, 12
    # Prepare |+>
    c.append("H 9 10 11 12")
    
    # S0: XXIXXIIII (0,1,3,4) -> Anc 9
    c.append("CX 9 0 9 1 9 3 9 4")
    # S1: IIIIXXIXX (4,5,7,8) -> Anc 10
    c.append("CX 10 4 10 5 10 7 10 8")
    # S2: IIXIIXIII (2,5,8)   -> Anc 11
    c.append("CX 11 2 11 5 11 8")
    # S3: IIIXIIXII (3,6,8)   -> Anc 12
    c.append("CX 12 3 12 6 12 8")
    
    # Measure in X (apply H then M in Z)
    c.append("H 9 10 11 12")
    
    # Z stabilizers: 13, 14, 15, 16
    # S4: IIIZZIZZI (3,4,6,7) -> Anc 13
    c.append("CX 3 13 4 13 6 13 7 13")
    # S5: IZZIZZIII (1,2,4,5) -> Anc 14
    c.append("CX 1 14 2 14 4 14 5 14")
    # S6: ZZIIIIIII (0,1)     -> Anc 15
    c.append("CX 0 15 1 15")
    # S7: IIIIIIIZZ (7,8)     -> Anc 16
    c.append("CX 7 16 8 16")
    
    # Measurement
    c.append("M 9 10 11 12 13 14 15 16")
    
    return "\n".join(c)

if __name__ == "__main__":
    print(get_circuit())
