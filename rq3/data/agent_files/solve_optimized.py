import stim
import sys
import random

def get_metrics(circuit):
    cx_count = 0
    volume = 0
    # Flatten the circuit to count operations correctly
    for op in circuit.flattened():
        name = op.name
        if name in ["CX", "CNOT"]:
            count = len(op.targets_copy()) // 2
            cx_count += count
            volume += count
        elif name in ["CY", "CZ", "SWAP", "ISWAP"]:
            count = len(op.targets_copy()) // 2
            volume += count # These count for volume but not CX count
        elif name in ["H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
            count = len(op.targets_copy())
            volume += count
        # Other gates (measurements, etc) might count, but usually not in volume for this context.
        # But let's count everything that is a gate.
    return cx_count, volume

def check_preservation(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    for s in stabilizers:
        if sim.peek_observable_expectation(s) != 1:
            return False
    return True

def main():
    try:
        # Load baseline
        baseline_path = r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\baseline.stim"
        with open(baseline_path, "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        base_cx, base_vol = get_metrics(baseline)
        
        print(f"Baseline: CX={base_cx}, Volume={base_vol}")
        
        # Load stabilizers
        stabilizers_path = r"C:\Users\anpaz\Repos\quantum-ai\rq3\stabilizers_task.txt"
        with open(stabilizers_path, "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        
        stabilizers = []
        for line in lines:
            stabilizers.append(stim.PauliString(line))
            
        best_circuit = None
        best_metrics = (base_cx, base_vol) # Start with baseline as reference
        found_better = False
        
        # Strategy 1: Direct synthesis
        print("Attempting direct synthesis (elimination)...")
        try:
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            circ = tableau.to_circuit(method="elimination")
            cx, vol = get_metrics(circ)
            print(f"Direct synthesis: CX={cx}, Volume={vol}")
            
            if check_preservation(circ, stabilizers):
                 if (cx < base_cx) or (cx == base_cx and vol < base_vol):
                    best_circuit = circ
                    best_metrics = (cx, vol)
                    found_better = True
                    print("Direct synthesis is strictly better and VALID.")
            else:
                 print("Direct synthesis result INVALID.")
        except Exception as e:
            print(f"Direct synthesis failed: {e}")

        # Strategy 2: Graph State synthesis
        print("Attempting graph_state synthesis...")
        try:
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            circ = tableau.to_circuit(method="graph_state")
            cx, vol = get_metrics(circ)
            print(f"Graph State synthesis: CX={cx}, Volume={vol}")
            
            if check_preservation(circ, stabilizers):
                if (cx < best_metrics[0]) or (cx == best_metrics[0] and vol < best_metrics[1]):
                    best_circuit = circ
                    best_metrics = (cx, vol)
                    found_better = True
                    print("Graph State synthesis is strictly better and VALID.")
            else:
                print("Graph State synthesis result INVALID.")

        except Exception as e:
            print(f"Graph State synthesis failed: {e}")

        # Strategy 3: Shuffled synthesis (try 20 times)
        print("Attempting shuffled synthesis...")
        for i in range(100):
            shuffled_stabs = stabilizers[:]
            random.shuffle(shuffled_stabs)
            try:
                # Re-creating tableau from shuffled list might produce different elimination order
                tableau = stim.Tableau.from_stabilizers(shuffled_stabs, allow_underconstrained=True)
                circ = tableau.to_circuit(method="elimination")
                cx, vol = get_metrics(circ)
                
                # Compare to current best
                if (cx < best_metrics[0]) or (cx == best_metrics[0] and vol < best_metrics[1]):
                    best_circuit = circ
                    best_metrics = (cx, vol)
                    found_better = True
                    print(f"New best found at iter {i}: CX={cx}, Volume={vol}")
            except Exception as e:
                continue

        if found_better and best_circuit:
            print("Strict improvement found!")
            print(f"Best metrics: CX={best_metrics[0]}, Volume={best_metrics[1]}")
            with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate_opt.stim", "w") as f:
                f.write(str(best_circuit))
        else:
            print("No strictly better circuit found.")
            # Still save the best candidate found (even if not strictly better than baseline, 
            # though loop logic prevents that unless direct synthesis failed and baseline was best).
            # If nothing better found, we might want to just output the baseline or the best attempt.
            if best_circuit:
                 with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate_opt.stim", "w") as f:
                    f.write(str(best_circuit))
            else:
                 with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate_opt.stim", "w") as f:
                    f.write(str(baseline))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
