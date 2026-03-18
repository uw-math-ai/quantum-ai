import stim
import sys
import os
import random

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
    if len(stabilizers) > 0:
        print(f"Num Stabilizers: {len(stabilizers)}")
        print(f"Stabilizer Length: {len(stabilizers[0])}")

    candidates = []
    
    # Check if baseline preserves stabilizers
    sim = stim.TableauSimulator()
    sim.do(baseline)
    valid_base = True
    for s in stabilizers:
        if sim.peek_observable_expectation(s) != 1:
            # print(f"  Baseline fails stabilizer: {s}")
            valid_base = False
            break
    
    if valid_base:
        print("Baseline Valid: True")
    else:
        print("Baseline Valid: False")

    best_circ = None
    best_metrics = (base_cx, base_vol)
    
    # Strategy 1: Shuffle stabilizers
    print("Attempting synthesis with stabilizer shuffling...")
    
    # Try 500 shuffles
    for i in range(500):
        shuffled_stabs = list(stabilizers)
        random.shuffle(shuffled_stabs)
        
        try:
            t = stim.Tableau.from_stabilizers(shuffled_stabs, allow_underconstrained=True)
            circ = t.to_circuit(method="elimination")
            
            cx, vol = count_metrics(circ)
            
            # Quick check if it's potentially better
            is_better = False
            if cx < best_metrics[0]:
                is_better = True
            elif cx == best_metrics[0] and vol < best_metrics[1]:
                is_better = True
            
            if is_better:
                # Verify
                sim = stim.TableauSimulator()
                sim.do(circ)
                valid = True
                for s in stabilizers:
                    if sim.peek_observable_expectation(s) != 1:
                        valid = False
                        break
                
                if valid:
                    print(f"  Iteration {i}: IMPROVEMENT FOUND! CX={cx}, Vol={vol}")
                    best_metrics = (cx, vol)
                    best_circ = circ
                    
                    # Save intermediate result
                    with open("candidate.stim", "w") as f:
                        f.write(str(best_circ))
            
            elif i % 50 == 0:
                 pass # print(f"  Iteration {i}: CX={cx}, Vol={vol} (Best: {best_metrics})")

        except Exception as e:
            pass # Ignore failures

    # Strategy 2: Sort by weight
    print("Attempting synthesis with sorted stabilizers...")
    try:
        sorted_stabs = sorted(stabilizers, key=lambda s: s.weight)
        t = stim.Tableau.from_stabilizers(sorted_stabs, allow_underconstrained=True)
        circ = t.to_circuit(method="elimination")
        cx, vol = count_metrics(circ)
        
        is_better = False
        if cx < best_metrics[0]:
            is_better = True
        elif cx == best_metrics[0] and vol < best_metrics[1]:
            is_better = True

        if is_better:
             # Verify
            sim = stim.TableauSimulator()
            sim.do(circ)
            valid = True
            for s in stabilizers:
                if sim.peek_observable_expectation(s) != 1:
                    valid = False
                    break
            if valid:
                print(f"  Sorted (Weight): IMPROVEMENT FOUND! CX={cx}, Vol={vol}")
                best_metrics = (cx, vol)
                best_circ = circ
                with open("candidate.stim", "w") as f:
                    f.write(str(best_circ))
    except Exception as e:
        print(e)

    # Strategy 3: Reverse sort
    try:
        sorted_stabs = sorted(stabilizers, key=lambda s: s.weight, reverse=True)
        t = stim.Tableau.from_stabilizers(sorted_stabs, allow_underconstrained=True)
        circ = t.to_circuit(method="elimination")
        cx, vol = count_metrics(circ)
        
        is_better = False
        if cx < best_metrics[0]:
            is_better = True
        elif cx == best_metrics[0] and vol < best_metrics[1]:
            is_better = True
            
        if is_better:
             # Verify
            sim = stim.TableauSimulator()
            sim.do(circ)
            valid = True
            for s in stabilizers:
                if sim.peek_observable_expectation(s) != 1:
                    valid = False
                    break
            if valid:
                print(f"  Sorted (Reverse Weight): IMPROVEMENT FOUND! CX={cx}, Vol={vol}")
                best_metrics = (cx, vol)
                best_circ = circ
                with open("candidate.stim", "w") as f:
                    f.write(str(best_circ))
    except Exception as e:
        print(e)

    if best_circ:
        print("Saving best candidate to candidate.stim")
        with open("candidate.stim", "w") as f:
            f.write(str(best_circ))
    else:
        print("No strictly better candidate found.")

if __name__ == "__main__":
    solve()
