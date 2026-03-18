import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            count += len(instr.targets_copy()) // 2
    return count

def compute_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["H", "S", "CX", "CY", "CZ", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "CNOT", "SWAP", "ISWAP"]:
            n_args = len(instr.targets_copy())
            if instr.name in ["CX", "CY", "CZ", "CNOT", "SWAP", "ISWAP"]:
                count += n_args // 2
            else:
                count += n_args
    return count

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    return [stim.PauliString(l) for l in lines]

def verify_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = []
    failed = []
    for i, stab in enumerate(stabilizers):
        if sim.peek_observable_expectation(stab) == 1:
            preserved.append(i)
        else:
            failed.append(i)
    return preserved, failed

def main():
    try:
        circuit = stim.Circuit.from_file("candidate_perm.stim")
        stabilizers = load_stabilizers("stabilizers_54.txt")
        
        print(f"Loaded candidate with {len(circuit)} instructions.")
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        cx = count_cx(circuit)
        vol = compute_volume(circuit)
        print(f"Candidate Metrics: CX={cx}, Volume={vol}")
        
        # Baseline reference
        baseline_cx = 237
        baseline_vol = 250
        
        if cx < baseline_cx or (cx == baseline_cx and vol < baseline_vol):
            print("Candidate is STRICTLY BETTER.")
        else:
            print(f"Candidate is NOT better. (Baseline: {baseline_cx}, {baseline_vol})")
            
        preserved, failed = verify_stabilizers(circuit, stabilizers)
        if not failed:
            print("Candidate is VALID.")
        else:
            print(f"Candidate is INVALID. Failed: {len(failed)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
