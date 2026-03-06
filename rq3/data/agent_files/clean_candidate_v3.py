import stim
import sys

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
        if line.startswith("RX "):
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
        
        # Save as string
        with open("candidate_clean.stim", "w") as f:
            f.write(new_content)
        print("Cleaned circuit saved to candidate_clean.stim")
        
        # Verify preservation
        print("Verifying preservation...")
        try:
            # Use CORRECT filename
            with open("current_task_stabilizers.txt", "r") as f:
                stabilizers = [line.strip() for line in f if line.strip()]
            
            sim = stim.TableauSimulator()
            sim.do_circuit(circuit)
            
            failed = 0
            for i, s_str in enumerate(stabilizers):
                s = stim.PauliString(s_str)
                if sim.peek_observable_expectation(s) != 1:
                    print(f"FAIL: Stabilizer {i} not preserved.")
                    failed += 1
                    if failed > 5:
                        break
            
            if failed == 0:
                print("SUCCESS: All stabilizers preserved.")
            else:
                print(f"FAILURE: {failed} stabilizers not preserved.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Verification failed: {e}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Failed to parse cleaned circuit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
