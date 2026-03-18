import stim
import sys

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        n = len(instr.targets_copy())
        if instr.name in ['CX', 'CNOT']:
            cx_count += n // 2
            volume += n // 2
        elif instr.name in ['CZ', 'CY', 'SWAP']:
            volume += n // 2
        elif instr.name in ['H', 'S', 'S_DAG', 'SQRT_X', 'SQRT_X_DAG', 'SQRT_Y', 'SQRT_Y_DAG', 'X', 'Y', 'Z', 'I']:
            volume += n
    return cx_count, volume

def solve():
    # Load stabilizers
    with open('stabilizers_anpaz_v1.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = [stim.PauliString(s) for s in lines]
    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Load baseline
    with open('baseline_anpaz_v1.stim', 'r') as f:
        baseline_text = f.read()
    
    baseline = stim.Circuit(baseline_text)
    base_cx, base_vol = count_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")

    # Synthesize
    print("Reading candidate from file...")
    with open('candidate_anpaz_v1.stim', 'r') as f:
        cand_text = f.read()
    cand = stim.Circuit(cand_text)
    
    # Check metrics
    cx, vol = count_metrics(cand)
    print(f"Candidate Metrics: CX={cx}, Vol={vol}")

    # Check validity (preserves stabilizers)
    sim = stim.TableauSimulator()
    sim.do_circuit(cand)
    preserved = 0
    for s in stabilizers:
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
    print(f"Candidate preserved: {preserved}/{len(stabilizers)}")

    if preserved == len(stabilizers) and cx < base_cx:
        print("Candidate is VALID and STRICTLY BETTER.")
    elif preserved == len(stabilizers) and cx == base_cx and vol < base_vol:
        print("Candidate is VALID and STRICTLY BETTER (Volume).")
    else:
        print("Candidate is INVALID or NOT BETTER.")

if __name__ == "__main__":
    solve()
