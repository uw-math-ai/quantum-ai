import stim

def check_cx_count():
    with open("candidate_prompt.stim", "r") as f:
        c = stim.Circuit(f.read())
        
    print(f"Total gates: {len(c)}")
    cx = c.num_gates("CX")
    cz = c.num_gates("CZ")
    h = c.num_gates("H")
    s = c.num_gates("S")
    
    print(f"CX: {cx}")
    print(f"CZ: {cz}")
    print(f"H: {h}")
    print(f"S: {s}")
    
    if cx == 0 and cz > 0:
        print("Warning: Circuit uses CZ instead of CX. Verify harness accepts CZ.")

if __name__ == "__main__":
    check_cx_count()
