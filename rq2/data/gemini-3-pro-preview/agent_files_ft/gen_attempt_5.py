def generate_circuit():
    # Parts
    # p1 (Steps 1-4)
    p1 = "H 0 1 3\nCX 0 1 0 3 0 6"
    
    # Check 7 (Anc 16) Z7 Z8
    c7 = "CX 7 16 8 16"
    
    # p2 (Steps 5-8)
    p2 = "CX 0 8 6 1 1 6 6 1"
    
    # Check 6 (Anc 15) Z0 Z1, Check 3 (Anc 12) X3 X6 X8
    c6 = "CX 0 15 1 15"
    c3 = "H 12\nCX 12 3 12 6 12 8\nH 12"
    
    # p3 (Step 9)
    p3 = "CX 1 5"
    
    # Check 5 (Anc 14) Z1 Z2 Z4 Z5
    c5 = "CX 1 14 2 14 4 14 5 14"
    
    # p4 (Steps 10-11)
    p4 = "H 2\nCX 2 5"
    
    # Check 2 (Anc 11) X2 X5 X8
    c2 = "H 11\nCX 11 2 11 5 11 8\nH 11"
    
    # p5 (Steps 12-13)
    p5 = "CX 3 4 6 4"
    
    # Check 4 (Anc 13) Z3 Z4 Z6 Z7
    c4 = "CX 3 13 4 13 6 13 7 13"
    
    # p6 split
    # Step 14: 4 6. Step 15: 6 4. Step 16: 4 5.
    p6a = "CX 4 6 6 4 4 5"
    
    # Check 5_late (Anc 17) Z1 Z2 Z4 Z5
    c5_late = "CX 1 17 2 17 4 17 5 17"
    
    # Step 17: 4 6.
    p6b = "CX 4 6"
    
    # Check 4_late (Anc 18) Z3 Z4 Z6 Z7
    c4_late = "CX 3 18 4 18 6 18 7 18"
    
    # Step 18: 4 8.
    p6c = "CX 4 8"
    
    # Check 0 (Anc 9) X0 X1 X3 X4
    c0 = "H 9\nCX 9 0 9 1 9 3 9 4\nH 9"
    
    # p7 (Steps 19-21)
    p7 = "CX 7 6 8 6 8 7"
    
    # Check 1 (Anc 10) X4 X5 X7 X8
    c1 = "H 10\nCX 10 4 10 5 10 7 10 8\nH 10"
    
    # Check 6_late (Anc 19) Z0 Z1
    c6_late = "CX 0 19 1 19"
    
    # Check 7_late (Anc 20) Z7 Z8
    c7_late = "CX 7 20 8 20"
    
    # Measure
    meas = "M 9 10 11 12 13 14 15 16 17 18 19 20"
    
    return "\n".join([p1, c7, p2, c6, c3, p3, c5, p4, c2, p5, c4, p6a, c5_late, p6b, c4_late, p6c, c0, p7, c1, c6_late, c7_late, meas])

if __name__ == "__main__":
    print(generate_circuit())
