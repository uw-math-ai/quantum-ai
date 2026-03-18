import stim

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    stabilizers = []
    for line in lines:
        line = line.replace(',', '')
        stabilizers.append(stim.PauliString(line))
    return stabilizers

def main():
    print("Reading candidate.stim...")
    with open("candidate.stim", "r") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("RX"):
            # Replace RX with H
            # Example: RX 0 1 2 -> H 0 1 2
            new_lines.append(line.replace("RX", "H"))
        else:
            new_lines.append(line)
            
    circuit = stim.Circuit("".join(new_lines))
    
    print("Verifying fixed circuit...")
    stabilizers = load_stabilizers("stabilizers.txt")
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    all_good = True
    for i, stab in enumerate(stabilizers):
        if sim.peek_observable_expectation(stab) != 1:
            print(f"FAIL: Stabilizer {i} not preserved")
            all_good = False
            break
            
    if all_good:
        print("SUCCESS: All stabilizers preserved.")
        with open("candidate_fixed.stim", "w") as f:
            f.write(str(circuit))
        print("Saved to candidate_fixed.stim")
    else:
        print("FAILURE: Validation failed.")

if __name__ == "__main__":
    main()
