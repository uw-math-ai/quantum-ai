import stim
import sys

def verify():
    try:
        with open("candidate_perm.stim") as f:
            c_text = f.read()
        c = stim.Circuit(c_text)
    except Exception as e:
        print(f"Failed to load candidate: {e}")
        return

    print(f"Candidate gates: {len(c)}")
    cx = 0
    for op in c:
        if op.name in ["CX", "CNOT", "CY", "CZ", "SWAP"]:
            cx += len(op.targets_copy()) // 2
    print(f"Candidate CX: {cx}")
    
    print("Loading stabilizers...")
    with open("stabilizers.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabs = [stim.PauliString(s) for s in lines]
    
    sim = stim.TableauSimulator()
    sim.do(c)
    
    preserved = 0
    failed = []
    for i, s in enumerate(stabs):
        expect = sim.peek_observable_expectation(s)
        if expect == 1:
            preserved += 1
        else:
            failed.append((i, s, expect))
            
    print(f"Preserved: {preserved}/{len(stabs)}")
    
    if preserved == len(stabs):
        print("VERIFIED: All stabilizers preserved.")
    else:
        print(f"FAILED: {len(failed)} stabilizers not preserved.")
        # Print first few failures
        for i, s, expect in failed[:5]:
            print(f"  Stabilizer {i}: {s} -> Expectation {expect}")

if __name__ == "__main__":
    verify()
