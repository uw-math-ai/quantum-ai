import stim

# Re-run the exact logic of solve_133_v2 but with verbose logging
def solve_debug():
    print("Reading stabilizers...")
    with open("stabilizers_133.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(lines)} stabilizers")
    
    # Check if the failing string is in lines
    bad_stab = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII"
    if bad_stab in lines:
        print("Bad stabilizer FOUND in lines.")
    else:
        print("Bad stabilizer NOT FOUND in lines.")
        # Print lines that look like it
        for l in lines:
            if "XXXX" in l and l.endswith("IIIIIIIIIIIIIIIIIIIII"):
                print(f"Similar: {l}")

    stabilizers = [stim.PauliString(s) for s in lines]
    
    # Re-create tableau
    print("Creating tableau...")
    t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    c = t.to_circuit("elimination")
    
    # Verify
    sim = stim.TableauSimulator()
    sim.do(c)
    
    # Check specific bad stabilizer
    s = stim.PauliString(bad_stab)
    print(f"Expectation of bad stab: {sim.peek_observable_expectation(s)}")
    
    # Check all
    failed = 0
    for s_str in lines:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) != 1:
            failed += 1
    print(f"Total failed: {failed}")

if __name__ == "__main__":
    solve_debug()
