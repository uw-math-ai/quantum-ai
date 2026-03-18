import stim
import sys

def get_stabilizers():
    with open("stabilizers.txt", "r") as f:
        lines = [l.strip().replace(',', '') for l in f.read().splitlines() if l.strip()]
    return [stim.PauliString(l) for l in lines]

def solve():
    # 1. Process best_candidate.stim to final_candidate.stim
    try:
        with open("best_candidate.stim", "r") as f:
            best_str = f.read()
    except FileNotFoundError:
        print("best_candidate.stim not found!")
        sys.exit(1)
        
    circuit = stim.Circuit(best_str)
    new_circuit = stim.Circuit()
    
    # Check for RX/resets
    has_rx = False
    
    for op in circuit:
        if op.name == "RX":
            # Replace RX with H (assuming input |0>)
            # RX prepares |+>. H|0> = |+>.
            new_circuit.append("H", op.targets_copy())
            has_rx = True
        elif op.name == "R" or op.name == "RZ":
            # Reset Z. Input |0> -> |0>. No-op.
            pass
        elif op.name == "TICK":
            pass
        elif op.name == "QUBIT_COORDS":
            pass
        else:
            new_circuit.append(op)
            
    # Save final candidate
    final_str = str(new_circuit)
    with open("final_candidate.stim", "w") as f:
        f.write(final_str)
    
    print(f"Generated final_candidate.stim (replaced RX: {has_rx})")
    
    # 2. Verify stabilizers
    stabilizers = get_stabilizers()
    sim = stim.TableauSimulator()
    sim.do_circuit(new_circuit)
    
    all_preserved = True
    for i, stab in enumerate(stabilizers):
        ex = sim.peek_observable_expectation(stab)
        if ex != 1:
            print(f"Stabilizer {i} NOT preserved. Expectation: {ex}")
            all_preserved = False
            # break # Don't break, verify all
    
    if all_preserved:
        print("All stabilizers preserved locally!")
        
        # 3. Check metrics locally
        cx_count = 0
        volume = 0
        for op in new_circuit:
            if op.name == "CX":
                cx_count += len(op.targets_copy()) // 2
            
            if op.name in ["CX", "CY", "CZ", "SWAP"]:
                volume += len(op.targets_copy()) // 2
            elif op.name not in ["QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "SHIFT_COORDS", "TICK"]:
                volume += len(op.targets_copy())
        
        print(f"Metrics: CX={cx_count}, Vol={volume}")

    else:
        print("Verification FAILED.")

if __name__ == "__main__":
    solve()
