def get_baseline_parts():
    # Part 1
    p1 = "H 0 1 3\nCX 0 1 0 3 0 6 0 8"
    # Part 2
    p2 = "CX 6 1 1 6 6 1 1 5\nH 2\nCX 2 5 3 4 6 4 4 6 6 4 4 5 4 6 4 8 7 6 8 6 8 7"
    return p1, p2

def generate_circuit():
    p1, p2 = get_baseline_parts()
    
    # Ancillas 9-16
    # 15: ZZIIIIIII (0,1) Z -> Check between p1 and p2
    
    ops_early = []
    ops_late = []
    
    # Init ancillas implicitly
    
    # Check 15 early
    ops_early.append("CX 0 15 1 15")
    
    # Rest of checks at the end
    # X checks (9,10,11,12)
    ops_late.append("H 9 10 11 12")
    ops_late.append("CX 9 0 9 1 9 3 9 4")
    ops_late.append("CX 10 4 10 5 10 7 10 8")
    ops_late.append("CX 11 2 11 5 11 8")
    ops_late.append("CX 12 3 12 6 12 8")
    ops_late.append("H 9 10 11 12")
    
    # Z checks (13,14,16) - 15 is done
    ops_late.append("CX 3 13 4 13 6 13 7 13")
    ops_late.append("CX 1 14 2 14 4 14 5 14")
    # ops_late.append("CX 0 15 1 15") # Moved to early
    ops_late.append("CX 7 16 8 16")
    
    # Measure
    ops_late.append("M 9 10 11 12 13 14 15 16")
    
    return p1 + "\n" + "\n".join(ops_early) + "\n" + p2 + "\n" + "\n".join(ops_late)

if __name__ == "__main__":
    print(generate_circuit())
