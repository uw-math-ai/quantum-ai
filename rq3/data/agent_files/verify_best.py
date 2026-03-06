import stim

def load_stabilizers(filename):
    stabilizers = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))
    return stabilizers

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(stabilizers)
    failed = []
    
    for i, stab in enumerate(stabilizers):
        expectation = sim.peek_observable_expectation(stab)
        if expectation == 1:
            preserved += 1
        else:
            failed.append((i, str(stab), expectation))
            
    return preserved, total, failed

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "CXSWAP", "SWAPCX", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            count += len(op.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for op in circuit:
        if op.name in ["QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "SHIFT_COORDS", "TICK"]:
            continue
        targets = op.targets_copy()
        if op.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            count += len(targets) // 2
        else:
            count += len(targets)
    return count

def main():
    try:
        with open("best_candidate.stim", "r") as f:
            circuit = stim.Circuit(f.read())
        
        stabilizers = load_stabilizers("current_stabilizers.txt")
        
        print(f"Loaded {len(stabilizers)} target stabilizers.")
        
        preserved, total, failed = check_stabilizers(circuit, stabilizers)
        
        print(f"Best candidate preserves {preserved}/{total} stabilizers.")
        
        if failed:
            print("Failed stabilizers:")
            for i, s, exp in failed[:5]:
                print(f"  #{i}: {s} (exp={exp})")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more.")
        else:
            print("Best candidate is VALID.")
            
        cx = count_cx(circuit)
        vol = count_volume(circuit)
        print(f"Metrics: CX={cx}, Vol={vol}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
