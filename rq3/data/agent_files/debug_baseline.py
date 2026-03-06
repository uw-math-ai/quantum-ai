import stim
import sys

def solve():
    print("Loading data...")
    with open("my_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    stabilizers = [stim.PauliString(l) for l in lines]
    
    baseline = stim.Circuit.from_file("my_baseline.stim")
    
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    plus_one = 0
    minus_one = 0
    zero = 0
    
    for s in stabilizers:
        exp = sim.peek_observable_expectation(s)
        if exp == 1:
            plus_one += 1
        elif exp == -1:
            minus_one += 1
        else:
            zero += 1
            
    print(f"Baseline Stabilizer Check:")
    print(f"  +1: {plus_one}")
    print(f"  -1: {minus_one}")
    print(f"   0: {zero}")
    
    if zero == 0 and minus_one > 0:
        print("Baseline preserves all stabilizers but with some sign flips.")
    elif zero > 0:
        print("Baseline FAILS to stabilize some operators (expectation 0).")

    # Try synthesis from baseline
    t = stim.Tableau.from_circuit(baseline)
    circ = t.to_circuit(method="elimination")
    
    # Check metrics
    def get_metrics(c):
        cx = 0
        vol = 0
        for i in c:
            if i.name in ["CX", "CNOT"]:
                n = len(i.targets_copy()) // 2
                cx += n
                vol += n
            elif i.name in ["CY", "CZ", "SWAP", "ISWAP"]:
                vol += len(i.targets_copy()) // 2
            else:
                vol += len(i.targets_copy())
        return cx, vol

    base_cx, base_vol = get_metrics(baseline)
    new_cx, new_vol = get_metrics(circ)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    print(f"New:      CX={new_cx}, Vol={new_vol}")
    
    if new_cx < base_cx:
        print("Improvement found from baseline synthesis!")
        with open("candidate.stim", "w") as f:
            f.write(str(circ))

if __name__ == "__main__":
    solve()
