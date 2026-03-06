import stim

def main():
    try:
        with open("best_candidate.stim", "r") as f:
            cand_text = f.read()
        cand = stim.Circuit(cand_text)
        print(f"Candidate loaded. Qubits: {cand.num_qubits}")
    except Exception as e:
        print(f"Error loading candidate: {e}")
        return

    try:
        with open("target_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        stabs = [stim.PauliString(l) for l in lines]
        print(f"Loaded {len(stabs)} stabilizers.")
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    sim = stim.TableauSimulator()
    sim.do(cand)
    
    preserved_count = 0
    for i, s in enumerate(stabs):
        if sim.peek_observable_expectation(s) == 1:
            preserved_count += 1
        else:
            print(f"Stabilizer {i} NOT preserved.")
    
    print(f"Preserved {preserved_count}/{len(stabs)} stabilizers.")

    cx_count = 0
    cz_count = 0
    for instr in cand:
        if instr.name == "CX" or instr.name == "CNOT":
            cx_count += len(instr.targets_copy()) // 2
        elif instr.name == "CZ":
            cz_count += len(instr.targets_copy()) // 2
    print(f"Candidate CX count: {cx_count}")
    print(f"Candidate CZ count: {cz_count}")
    
    vol_count = 0
    for instr in cand:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
             if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                 vol_count += len(instr.targets_copy()) // 2
             else:
                 vol_count += len(instr.targets_copy())
    print(f"Candidate Volume: {vol_count}")

if __name__ == "__main__":
    main()
