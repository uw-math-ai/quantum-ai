import stim

def check():
    with open("baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
        
    sim = stim.TableauSimulator()
    sim.do_circuit(baseline)
    
    # Construct fixed stabilizer 42
    # Original: XXXIIIIXXXIIIIIIIIIIIXXXIIIIXXXIIIIIIIIIII
    # Target:   XXXIIIIXXXIIIIIIIIIIIIIIIIIIXXXIIIIXXXIIIIIIIIIII
    # (Insert 7 Is at index 17?)
    # Let's verify the gap.
    # Original indices: 0-2(X), 3-6(I), 7-9(X), 10-20(I, len 11), 21-23(X), ...
    # Target indices:   0-2(X), 3-6(I), 7-9(X), 10-27(I, len 18), 28-30(X), ...
    
    # So we replace the gap of 11 Is with 18 Is.
    
    s42_fixed = "XXXIIIIXXX" + "I"*18 + "XXXIIIIXXXIIIIIIIIIII"
    print(f"Fixed S42: {s42_fixed}")
    print(f"Length: {len(s42_fixed)}")
    
    p = stim.PauliString(s42_fixed)
    if sim.peek_observable_expectation(p) == 1:
        print("SUCCESS: Baseline preserves Fixed Stabilizer 42")
    else:
        print("FAILURE: Baseline does NOT preserve Fixed Stabilizer 42")
        
    # Check if this fixed S42 commutes with S45 (Line 46)
    # S45: ZZZIIIIZZZIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIIIIIIII
    s45 = "ZZZIIIIZZZIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIIIIIIII"
    p45 = stim.PauliString(s45)
    
    if p.commutes(p45):
        print("SUCCESS: Fixed S42 commutes with S45")
    else:
        print("FAILURE: Fixed S42 anticommutes with S45")

if __name__ == "__main__":
    check()
