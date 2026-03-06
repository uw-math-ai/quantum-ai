import stim
import collections

def count_ops(circuit):
    counts = collections.Counter()
    vol = 0
    arity_map = {
        "CX": 2, "CNOT": 2, "CZ": 2, "CY": 2, "SWAP": 2,
        "H": 1, "S": 1, "S_DAG": 1, "X": 1, "Y": 1, "Z": 1, "RX": 1, "RY": 1, "RZ": 1, "I": 1,
        "SQRT_X": 1, "SQRT_X_DAG": 1, "SQRT_Y": 1, "SQRT_Y_DAG": 1
    }
    
    for op in circuit.flattened():
        name = op.name
        n = len(op.targets_copy())
        arity = arity_map.get(name, 1)
        
        num_ops = n // arity
        counts[name] += num_ops
        
        # Volume metric: sum of all gates in volume set
        if name in ["CX", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "X", "Y", "Z", "CNOT"]:
            vol += num_ops
            
    return counts, vol

def clean_and_check():
    try:
        with open("solution.stim", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("solution.stim not found!")
        return
        
    circ = stim.Circuit(content)
    new_circ = stim.Circuit()
    
    # Process instructions
    for op in circ: 
        name = op.name
        targets = op.targets_copy()
        args = op.gate_args_copy()
        
        if name == "RX":
            # Replace RX with H. Assume start state |0>.
            new_circ.append("H", targets)
        elif name == "TICK":
            continue
        else:
            new_circ.append(name, targets, args)
            
    # Save
    out_str = str(new_circ)
    with open("candidate_anpaz.stim", "w") as f:
        f.write(out_str)
        
    print("Candidate cleaned and saved to candidate_anpaz.stim.")
    
    # Metrics
    counts, vol = count_ops(new_circ)
    cx_count = counts['CX'] + counts['CNOT']
    cz_count = counts['CZ']
    print(f"Metrics for candidate_anpaz.stim:")
    print(f"  CX Count: {cx_count}")
    print(f"  CZ Count: {cz_count}")
    print(f"  Volume:   {vol}")
    
    if cx_count == 0:
        print("SUCCESS: CX count is 0. This is optimal.")
    else:
        print("WARNING: CX count is > 0.")

if __name__ == "__main__":
    clean_and_check()
