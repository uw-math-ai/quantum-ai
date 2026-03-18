import stim
import re

def main():
    with open("candidate_v100.stim", "r") as f:
        content = f.read()
    
    # Replace RX with H
    # We assume RX is used for initialization at the start
    # RX 0 1 ... -> H 0 1 ...
    # Be careful not to replace RX inside comments or something, but Stim doesn't have inline comments like that.
    # Also RX might appear later?
    # But graph state synthesis only puts RX at start if at all.
    # Let's just replace "RX " with "H ".
    
    # Stim format: "RX 0 1"
    # We want "H 0 1"
    
    # Check if RX is present
    if "RX" in content:
        print("Replacing RX with H...")
        new_content = content.replace("RX ", "H ")
    else:
        print("No RX found.")
        new_content = content
        
    with open("candidate_final.stim", "w") as f:
        f.write(new_content)
        
    # Verify
    print("Verifying candidate_final.stim...")
    
    # Load stabilizers
    with open("target_stabilizers_v100.txt", "r") as f:
        s_content = f.read().strip()
        stabilizers_str = [s.strip() for s in s_content.split(',') if s.strip()]
    
    # Load circuit
    circuit = stim.Circuit(new_content)
        
    # Simulate
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check expectations
    failed = False
    for i, s_str in enumerate(stabilizers_str):
        p = stim.PauliString(s_str)
        exp = sim.peek_observable_expectation(p)
        if exp != 1:
            print(f"Stabilizer {i} FAILED: expectation {exp}")
            failed = True
            break
            
    if not failed:
        print("All stabilizers preserved (expectation +1).")
    else:
        print("Verification FAILED.")

if __name__ == "__main__":
    main()
