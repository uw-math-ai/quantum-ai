import stim
import sys

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

def solve():
    print("Loading baseline...")
    try:
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\data\\agent_files\\baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    base_cx = count_cx(baseline)
    base_vol = count_volume(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")

    # Get canonical stabilizers from baseline state
    print("Computing stabilizers from baseline...")
    sim = stim.TableauSimulator()
    sim.do(baseline)
    stabilizers = sim.canonical_stabilizers()
    
    # Create tableau for the state
    print("Creating state tableau...")
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers)
    except Exception as e:
        print(f"Error creating tableau from stabilizers: {e}")
        return

    candidates = []

    # Method 1: Elimination
    print("Synthesizing with method='elimination'...")
    try:
        c1 = tableau.to_circuit(method="elimination")
        candidates.append(("elimination", c1))
    except Exception as e:
        print(f"Error with elimination: {e}")

    # Method 2: Graph State
    print("Synthesizing with method='graph_state'...")
    try:
        c2 = tableau.to_circuit(method="graph_state")
        candidates.append(("graph_state", c2))
    except Exception as e:
        print(f"Error with graph_state: {e}")

    # Analyze candidates
    best_circuit = None
    best_name = "baseline"
    best_cx = base_cx
    best_vol = base_vol
    
    found_improvement = False

    for name, cand in candidates:
        cx = count_cx(cand)
        vol = count_volume(cand)
        print(f"Candidate ({name}): CX={cx}, Vol={vol}")
        
        if cx < base_cx or (cx == base_cx and vol < base_vol):
            # Check if strictly better than current best candidate (if any)
            if best_circuit is None:
                best_circuit = cand
                best_name = name
                best_cx = cx
                best_vol = vol
                found_improvement = True
            else:
                 if cx < best_cx or (cx == best_cx and vol < best_vol):
                    best_circuit = cand
                    best_name = name
                    best_cx = cx
                    best_vol = vol
                    found_improvement = True

    if found_improvement:
        print(f"Strict improvement found with {best_name}: CX={best_cx}, Vol={best_vol}")
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\data\\agent_files\\optimized.stim", "w") as f:
            f.write(str(best_circuit))
        print("---CIRCUIT START---")
        print(str(best_circuit))
        print("---CIRCUIT END---")
    else:
        print("No strictly better circuit found.")
        # Save baseline as fallback? No, we shouldn't overwrite if not better.
        # But we need to verify stabilizer preservation for the baseline if we fail?
        # The prompt implies we must submit *something*.
        # If no improvement, we can't submit a "strictly better" one.
        # But maybe we can try one more thing:
        # Check if `tableau.inverse().to_circuit()` is better? No, that's inverse.
        
if __name__ == "__main__":
    solve()
