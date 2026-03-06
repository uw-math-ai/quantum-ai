import stim
import re

def main():
    try:
        with open("candidate.stim", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("candidate.stim not found.")
        return

    lines = content.splitlines()
    new_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("TICK"):
            continue
        
        # Replace RX with H
        # Regex to match RX at start of line
        if line.startswith("RX "):
            # Check if it's RX or R something else
            # RX followed by space
            new_line = "H " + line[3:]
            new_lines.append(new_line)
        else:
            new_lines.append(line)
            
    new_content = "\n".join(new_lines)
    
    try:
        # Check if parseable
        circuit = stim.Circuit(new_content)
        print("Cleaned circuit parsed successfully.")
        
        # Save as string to avoid decomposition
        with open("candidate_clean.stim", "w") as f:
            f.write(new_content)
        print("Cleaned circuit saved to candidate_clean.stim")
        
        # Verify preservation
        print("Verifying preservation...")
        try:
            with open("current_stabilizers_task.txt", "r") as f:
                stabilizers = [stim.PauliString(l.strip()) for l in f if l.strip()]
            
            sim = stim.TableauSimulator()
            sim.do_circuit(circuit)
            
            preserved = True
            for s in stabilizers:
                if sim.peek_observable_expectation(s) != 1:
                    preserved = False
                    print(f"FAIL: Stabilizer {s} not preserved.")
                    break
            
            if preserved:
                print("SUCCESS: All stabilizers preserved.")
            else:
                print("FAILURE: Stabilizers not preserved.")
                
        except Exception as e:
            print(f"Verification failed: {e}")
            
    except Exception as e:
        print(f"Failed to parse cleaned circuit: {e}")

if __name__ == "__main__":
    main()
