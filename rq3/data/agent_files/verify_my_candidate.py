import stim

BASELINE_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq3\current_baseline.stim"
CANDIDATE_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate_test.stim"
CLEAN_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate_clean.stim"
STABILIZERS_FILE = r"C:\Users\anpaz\Repos\quantum-ai\rq3\current_stabilizers.txt"

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit:
        name = instruction.name
        n_targets = len(instruction.targets_copy())
        
        if name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            gate_count = n_targets // 2
            if name in ["CX", "CNOT"]:
                cx += gate_count
            vol += gate_count
        elif name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"]:
             vol += n_targets
    return cx, vol

def clean_circuit(circuit):
    new_circuit = stim.Circuit()
    for instruction in circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        args = instruction.gate_args_copy()
        
        if name == "TICK":
            continue
        elif name == "RX":
            # Assume input |0>, RX -> H
            new_circuit.append("H", targets, args)
        elif name == "RY":
            # Assume input |0>, RY -> H S
            new_circuit.append("H", targets, args)
            new_circuit.append("S", targets, args)
        elif name == "R" or name == "RZ":
            # Assume input |0>, R/RZ -> I (nothing)
            pass
        else:
            new_circuit.append(name, targets, args)
    return new_circuit

def main():
    try:
        with open(BASELINE_FILE, "r") as f:
            baseline = stim.Circuit(f.read())
    except FileNotFoundError:
        print(f"Error: {BASELINE_FILE} not found.")
        return

    try:
        with open(CANDIDATE_FILE, "r") as f:
            candidate = stim.Circuit(f.read())
    except FileNotFoundError:
        print(f"Error: {CANDIDATE_FILE} not found.")
        return

    cleaned = clean_circuit(candidate)
    
    # Load stabilizers
    stabilizers = []
    try:
        with open(STABILIZERS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    stabilizers.append(stim.PauliString(line))
    except FileNotFoundError:
        print(f"Error: {STABILIZERS_FILE} not found.")
        return
        
    print(f"Checking {len(stabilizers)} stabilizers...")
    
    sim = stim.TableauSimulator()
    sim.do(cleaned)
    
    valid = True
    for s in stabilizers:
        if sim.peek_observable_expectation(s) != 1:
            print(f"Failed stabilizer: {s}")
            valid = False
            # break # Don't break, see how many fail
            
    if valid:
        print("All stabilizers preserved!")
        
        base_cx, base_vol = get_metrics(baseline)
        clean_cx, clean_vol = get_metrics(cleaned)
        
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        print(f"Cleaned:  CX={clean_cx}, Vol={clean_vol}")
        
        if clean_cx < base_cx or (clean_cx == base_cx and clean_vol < base_vol):
            print("Improvement confirmed.")
            with open(CLEAN_FILE, "w") as f:
                f.write(str(cleaned))
        else:
            print("No improvement.")
    else:
        print("Stabilizer check failed.")

if __name__ == "__main__":
    main()
