import stim

def verify():
    try:
        with open("cleaned_candidate.stim", "r") as f:
            content = f.read()
            circ = stim.Circuit(content)
        
        with open("stabilizers.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
            
        print(f"Checking {len(stabilizers)} stabilizers...")
        
        sim = stim.TableauSimulator()
        sim.do(circ)
        
        valid = True
        failed = 0
        for i, s in enumerate(stabilizers):
            if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
                # print(f"Stabilizer {i} failed")
                valid = False
                failed += 1
                
        if valid:
            print("VALID: All stabilizers preserved.")
        else:
            print(f"INVALID: {failed} stabilizers failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
