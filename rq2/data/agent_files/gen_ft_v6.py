
def get_circuit():
    c = "H 0\nCX 0 1 0 2 0 3 2 1 3 1\n"
    
    # XXXX check (anc 4) - catch Z
    c += "H 4\nCX 4 0 4 1 4 2 4 3\nH 4\n"
    
    # Z0Z1 check (anc 5) - catch X
    c += "CX 0 5 1 5\n"
    
    # Z1Z2 check (anc 6)
    c += "CX 1 6 2 6\n"
    
    # Z2Z3 check (anc 7)
    c += "CX 2 7 3 7\n"

    # ZZZZ check (anc 8) - global catch X
    c += "CX 0 8 1 8 2 8 3 8\n"
    
    # XXXX check (anc 9) - catch Z from Z-checks
    c += "H 9\nCX 9 0 9 1 9 2 9 3\nH 9\n"
    
    c += "M 4 5 6 7 8 9"
    return c

print(get_circuit())
