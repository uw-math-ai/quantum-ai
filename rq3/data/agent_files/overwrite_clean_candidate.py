import stim

def solve():
    try:
        with open("best_candidate.stim", "r") as f:
            lines = f.readlines()
    except:
        print("Error reading best_candidate.stim")
        return

    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("RX"):
            # Replace RX with H
            # Ensure we keep the arguments
            args = stripped[3:]
            new_line = "H " + args + "\n"
            new_lines.append(new_line)
        elif stripped.startswith("TICK"):
            continue
        else:
            new_lines.append(line)
            
    with open("candidate_clean.stim", "w") as f:
        f.writelines(new_lines)
        
    print("Cleaned candidate saved to candidate_clean.stim")
    
    # Verify
    try:
        cand_str = "".join(new_lines)
        cand = stim.Circuit(cand_str)
        print("Candidate parses successfully.")
        
        # Load stabs
        with open("target_stabilizers.txt", "r") as f:
            stabs = [stim.PauliString(l.strip()) for l in f if l.strip()]
        
        print(f"Checking {len(stabs)} stabilizers...")
        
        sim = stim.TableauSimulator()
        sim.do(cand)
        
        preserved = True
        failed_count = 0
        for s in stabs:
            if sim.peek_observable_expectation(s) != 1:
                preserved = False
                failed_count += 1
                # print(f"Failed: {s}")
                
        if preserved:
            print("Candidate preserves stabilizers.")
        else:
            print(f"Candidate DOES NOT preserve stabilizers. Failed: {failed_count}")
            
        cx_count = 0
        for instr in cand:
            if instr.name == "CX" or instr.name == "CNOT":
                cx_count += len(instr.targets_copy()) // 2
        print(f"CX count: {cx_count}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
