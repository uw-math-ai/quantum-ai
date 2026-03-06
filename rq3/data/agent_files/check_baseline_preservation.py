import stim

def main():
    try:
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        print(f"Baseline loaded. Qubits: {baseline.num_qubits}")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    try:
        with open("target_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        stabs = [stim.PauliString(l) for l in lines]
        print(f"Loaded {len(stabs)} stabilizers.")
        if len(stabs) > 0:
            print(f"Stabilizer length: {len(stabs[0])}")
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    preserved_count = 0
    for i, s in enumerate(stabs):
        if sim.peek_observable_expectation(s) == 1:
            preserved_count += 1
        else:
            print(f"Stabilizer {i} NOT preserved.")
    
    print(f"Preserved {preserved_count}/{len(stabs)} stabilizers.")

    cx_count = 0
    for instr in baseline:
        if instr.name == "CX":
            cx_count += len(instr.targets_copy()) // 2
    print(f"Baseline CX count: {cx_count}")
    
    vol_count = 0
    for instr in baseline:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
             if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                 vol_count += len(instr.targets_copy()) // 2
             else:
                 vol_count += len(instr.targets_copy())
    print(f"Baseline Volume: {vol_count}")

if __name__ == "__main__":
    main()
