import stim
import sys

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            n_targets = len(instruction.targets_copy())
            count = n_targets // 2
            vol += count
            if instruction.name in ["CX", "CNOT"]:
                cx += count
        else:
            if instruction.name not in ["TICK", "SHIFT_COORDS", "QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE"]:
                 n_targets = len(instruction.targets_copy())
                 vol += n_targets
    return cx, vol

def main():
    # Load candidate
    with open("best_candidate.stim", "r") as f:
        content = f.read()
    
    c = stim.Circuit(content)
    new_c = stim.Circuit()
    
    # Replace RX with H
    for instruction in c:
        if instruction.name == "RX":
            new_c.append("H", instruction.targets_copy())
        else:
            new_c.append(instruction)
            
    # Check metrics
    cx, vol = get_metrics(new_c)
    print(f"Metrics: CX={cx}, Vol={vol}")
    
    # Verify stabilizers
    with open("stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    sim = stim.TableauSimulator()
    sim.do(new_c)
    
    valid = True
    for s in stabs:
        if not sim.peek_observable_expectation(stim.PauliString(s)) == 1:
            valid = False
            print(f"Failed to preserve {s}")
            break
            
    if valid:
        print("Stabilizers PRESERVED.")
        with open("final_submission.stim", "w") as f:
            f.write(str(new_c))
    else:
        print("Stabilizers NOT preserved.")
        sys.exit(1)

if __name__ == "__main__":
    main()
