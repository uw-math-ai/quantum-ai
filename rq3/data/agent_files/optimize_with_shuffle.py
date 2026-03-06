import stim
import random

def get_metrics(circuit):
    real_cx = 0
    real_vol = 0
    for op in circuit.flattened():
        n = 0
        if op.name in ["CX", "CNOT", "CZ", "CY", "XC", "YC", "ZC", "SWAP", "ISWAP"]:
            n = 2
        else:
            n = 1
        
        count = len(op.targets_copy()) // n
        real_vol += count
        if op.name == "CX" or op.name == "CNOT":
            real_cx += count
            
    return real_cx, real_vol

def check_circuit(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    for s in stabilizers:
        if sim.peek_observable_expectation(s) != 1:
            return False
    return True

def run():
    print("Loading baseline...")
    with open("my_baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    base_cx, base_vol = get_metrics(baseline)
    print(f"Baseline CX: {base_cx}, Vol: {base_vol}")

    with open("current_stabilizers.txt", "r") as f:
         stabs = [stim.PauliString(s.strip()) for s in f if s.strip()]
    
    best_cx = base_cx
    best_vol = base_vol
    best_circ = None
    
    # Try original order first
    tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
    circ = tableau.to_circuit(method="elimination")
    cx, vol = get_metrics(circ)
    print(f"Original order: CX={cx}, Vol={vol}")
    if cx < best_cx or (cx == best_cx and vol < best_vol):
        best_cx = cx
        best_vol = vol
        best_circ = circ

    # Try shuffling
    for i in range(500):
        random.shuffle(stabs)
        try:
            tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
            circ = tableau.to_circuit(method="elimination")
            cx, vol = get_metrics(circ)
            
            if cx < best_cx:
                print(f"Found better CX: {cx} (iter {i})")
                best_cx = cx
                best_vol = vol
                best_circ = circ
            elif cx == best_cx and vol < best_vol:
                print(f"Found better Vol: {vol} (CX {cx}) (iter {i})")
                best_vol = vol
                best_circ = circ
        except Exception:
            continue
            
    if best_circ:
        print(f"Best found: CX={best_cx}, Vol={best_vol}")
        # Verify
        # Need to re-read original stabilizers because shuffling modified the list in place?
        # Yes, random.shuffle modifies in place.
        # But for check_circuit, order doesn't matter.
        if check_circuit(best_circ, stabs): # stabs is shuffled but set is same
            print("VALID")
            with open("candidate.stim", "w") as f:
                f.write(str(best_circ))
        else:
            print("INVALID (should not happen with stim synthesis)")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    run()
