import stim
import sys
import os

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT"]:
            n = len(instruction.targets_copy()) // 2
            cx += n
            vol += n
        elif instruction.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
             n = len(instruction.targets_copy()) // 2
             vol += n
        else:
             # Single qubit gates
             vol += len(instruction.targets_copy())
    return cx, vol

def solve():
    print("Loading data...")
    try:
        with open("current_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        stabilizers = [stim.PauliString(l) for l in lines]
        
        baseline = stim.Circuit.from_file("current_baseline.stim")
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    base_cx, base_vol = count_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}, Qubits={baseline.num_qubits}")

    candidates = []

    # Method 1: Synthesis from stabilizers (State Preparation)
    print("Attempting synthesis from stabilizers...")
    try:
        # allow_underconstrained=True allows for partial stabilizer sets (pure states or mixed states)
        # But we want to satisfy ALL stabilizers.
        t_stabs = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circ_stabs = t_stabs.to_circuit(method="elimination")
        candidates.append(("from_stabilizers", circ_stabs))
    except Exception as e:
        print(f"Failed synthesis from stabilizers: {e}")

    # Method 2: Synthesis from baseline tableau (Unitary Synthesis)
    print("Attempting synthesis from baseline tableau...")
    try:
        t_base = stim.Tableau.from_circuit(baseline)
        circ_base = t_base.to_circuit(method="elimination")
        candidates.append(("from_baseline", circ_base))
    except Exception as e:
        print(f"Failed synthesis from baseline: {e}")

    best_circ = None
    best_metrics = (base_cx, base_vol)
    
    # Evaluate candidates
    for name, circ in candidates:
        cx, vol = count_metrics(circ)
        print(f"Candidate {name}: CX={cx}, Vol={vol}")
        
        # Check stabilizer preservation
        sim = stim.TableauSimulator()
        sim.do(circ)
        valid = True
        preserved = 0
        for s in stabilizers:
            if sim.peek_observable_expectation(s) != 1:
                valid = False
                # print(f"  Failed stabilizer: {s}")
                break
            preserved += 1
        
        if valid:
            print(f"  Valid: Preserved {preserved}/{len(stabilizers)} stabilizers.")
            
            # Check optimization
            is_better = False
            if cx < best_metrics[0]:
                is_better = True
            elif cx == best_metrics[0] and vol < best_metrics[1]:
                is_better = True
            
            if is_better:
                print(f"  Strictly better than current best ({best_metrics})!")
                best_metrics = (cx, vol)
                best_circ = circ
        else:
            print(f"  INVALID: Preserved {preserved}/{len(stabilizers)} stabilizers.")

    if best_circ:
        print("Saving best candidate to candidate.stim")
        with open("candidate.stim", "w") as f:
            f.write(str(best_circ))
    else:
        print("No better candidate found.")

if __name__ == "__main__":
    solve()
