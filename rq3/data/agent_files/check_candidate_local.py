import stim
import sys

def check():
    print("Loading stabilizers...")
    with open("current_task_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    print("Loading candidate...")
    with open("best_candidate.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    # print(f"Circuit gates: {circuit.num_gates('CX')} CX, {circuit.num_gates('CZ')} CZ")
    cx = 0
    cz = 0
    for instr in circuit:
        if instr.name == "CX":
            cx += len(instr.targets_copy()) // 2
        elif instr.name == "CZ":
            cz += len(instr.targets_copy()) // 2
    print(f"Circuit gates: {cx} CX, {cz} CZ")
    
    # Verify stabilizers
    print("Verifying stabilizers...")
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    all_good = True
    for i, s in enumerate(stabilizers):
        pauli = stim.PauliString(s)
        expect = sim.peek_observable_expectation(pauli)
        if expect != 1:
            print(f"FAIL: Stabilizer {i} not preserved. Expectation: {expect}")
            all_good = False
            # break # Keep checking to see how many fail
    
    if all_good:
        print("SUCCESS: All stabilizers preserved.")
    else:
        print("FAILURE: Some stabilizers not preserved.")

if __name__ == "__main__":
    check()
