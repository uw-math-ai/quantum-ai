import stim

def verify():
    print("Verifying candidate_improved.stim...")
    try:
        # Check candidate
        with open("candidate_improved.stim", "r") as f:
            circ_text = f.read()
        circ = stim.Circuit(circ_text)
        
        # Check stabilizers
        with open("prompt_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        stabilizers = []
        for l in lines:
            if "," in l:
                parts = l.split(",")
                s = stim.PauliString(parts[-1].strip())
            else:
                s = stim.PauliString(l)
            stabilizers.append(s)
            
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Sim
        sim = stim.TableauSimulator()
        sim.do(circ)
        
        valid = True
        for i, s in enumerate(stabilizers):
            if sim.peek_observable_expectation(s) != 1:
                valid = False
                print(f"Failed stabilizer {i}")
                break
        
        if valid:
            print("Candidate is VALID.")
            
            # Count CX
            cx = 0
            vol = 0
            for instr in circ:
                if instr.name == "CX":
                    n = len(instr.targets_copy()) // 2
                    cx += n
                    vol += n
                elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
                    n = len(instr.targets_copy()) // 2
                    vol += n
                else:
                    vol += len(instr.targets_copy())
            print(f"CX count: {cx}")
            print(f"Volume: {vol}")
            
        else:
            print("Candidate is INVALID.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
