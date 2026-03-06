import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets_copy()) // 2
        elif instruction.name == "CZ":
            # Just to know
            pass
    return count

def count_cz(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CZ":
            count += len(instruction.targets_copy()) // 2
    return count

def check_preservation(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    failed = []
    for i, s_str in enumerate(stabilizers):
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
        else:
            failed.append(i)
    return preserved == len(stabilizers), preserved, failed

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip().replace(',', '') for l in f.readlines() if l.strip()]
    stabilizers = []
    for line in lines:
        parts = line.split()
        for p in parts:
            if set(p).issubset({'I', 'X', 'Y', 'Z'}):
                stabilizers.append(p)
    return stabilizers

def main():
    try:
        baseline = stim.Circuit.from_file("baseline_task.stim")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    stabilizers = load_stabilizers("target_stabilizers_task.txt")
    print(f"Loaded {len(stabilizers)} stabilizers.")

    base_cx = count_cx(baseline)
    base_cz = count_cz(baseline)
    print(f"Baseline CX count: {base_cx}")
    print(f"Baseline CZ count: {base_cz}")
    print(f"Baseline instructions: {len(baseline)}")

    is_valid, preserved_count, failed = check_preservation(baseline, stabilizers)
    print(f"Baseline valid: {is_valid} ({preserved_count}/{len(stabilizers)})")
    if not is_valid:
        print(f"Baseline failed stabilizers: {failed}")

    # Attempt 1: Graph State Synthesis
    tableau = stim.Tableau.from_circuit(baseline)
    
    best_cx = base_cx
    best_circuit = None
    best_method = "none"

    methods = ["graph_state", "elimination"]
    
    for method in methods:
        try:
            cand = tableau.to_circuit(method=method)
            cx = count_cx(cand)
            cz = count_cz(cand)
            print(f"Method {method}: CX={cx}, CZ={cz}")
            
            is_valid_cand, preserved_cand, _ = check_preservation(cand, stabilizers)
            print(f"Method {method} valid: {is_valid_cand}")
            
            if is_valid_cand:
                if cx < best_cx:
                    best_cx = cx
                    best_circuit = cand
                    best_method = method
        except Exception as e:
            print(f"Method {method} failed: {e}")

    if best_circuit is not None:
        print(f"FOUND BETTER CIRCUIT via {best_method} with CX={best_cx}")
        with open("candidate_task.stim", "w") as f:
            f.write(str(best_circuit))
    else:
        print("No better circuit found.")

if __name__ == "__main__":
    main()
