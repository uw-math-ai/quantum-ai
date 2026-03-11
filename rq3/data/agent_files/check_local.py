import stim

def check():
    with open("target_stabilizers.txt") as f:
        targets = [line.strip() for line in f if line.strip()]
        
    with open("candidate.stim") as f:
        circuit = stim.Circuit(f.read())
        
    # Check stabilizers
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    valid = True
    for s in targets:
        p = stim.PauliString(s)
        if sim.peek_observable_expectation(p) != 1:
            print(f"Failed stabilizer: {s}")
            valid = False
            break
            
    if valid:
        print("All stabilizers preserved.")
    else:
        print("Stabilizers NOT preserved.")
        
    # Check metrics
    cx_count = circuit.num_gates("CX")
    print(f"CX count: {cx_count}")
    
    # Volume check (approximate)
    volume_set = {"CX", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z"} # Check tool definition
    vol = 0
    for instr in circuit:
        if instr.name in volume_set:
            vol += len(instr.targets_copy()) # Approximation: some 2-qubit gates count as 1 op? No, usually gate count.
            # But wait, CZ 0 1 2 3 counts as 2 gates?
            # Tool says "total gate count".
            # Stim instruction with multiple targets is multiple gates.
            # E.g. H 0 1 is 2 H gates.
            if instr.name in ["CX", "CY", "CZ"]:
                vol += len(instr.targets_copy()) // 2
            else:
                vol += len(instr.targets_copy())
                
    print(f"Volume: {vol}")

if __name__ == "__main__":
    check()
