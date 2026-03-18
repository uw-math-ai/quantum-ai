import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def count_volume(circuit):
    # Approximating volume as total gate count
    return sum(1 for inst in circuit)

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for i, s_str in enumerate(stabilizers):
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
        else:
            print(f"Failed Stabilizer {i}: {s_str}")
            
    return preserved, total

def solve():
    print("Loading baseline...")
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    print("Loading stabilizers...")
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    print(f"Baseline CX: {count_cx(baseline)}")
    print(f"Baseline Volume: {count_volume(baseline)}")
    
    p, t = check_stabilizers(baseline, stabilizers)
    print(f"Baseline Preserved: {p}/{t}")
    
    if p != t:
        print("WARNING: Baseline does not preserve all stabilizers!")
        
    # Attempt 1: Resynthesis using Tableau
    # We want a circuit that prepares the state stabilized by 'stabilizers'.
    # Note: stabilizers provided are a generating set (hopefully).
    # If they are not independent, from_stabilizers might complain or drop some.
    
    print("Starting optimization search (reordering stabilizers)...")
    
    import random
    
    best_cx = 273
    best_circuit = None
    
    # Try the original order first (we know it gives 273)
    # Try random shuffles
    
    # We need to keep the stabilizers fixed, but we can feed them in different orders to from_stabilizers.
    # from_stabilizers maps Z_0 -> stab[0], Z_1 -> stab[1], etc.
    # The resulting circuit prepares the same state (up to global phase/logical operators).
    
    # If the system is underconstrained (48 stabs, 49 qubits), there is 1 logical qubit.
    # The state prepared is a stabilizer state of the group <S1...Sk>.
    # The specific mapping Z_i -> S_pi(i) affects the circuit structure.
    
    # Try 5000 iterations
    for attempt in range(5000):
        if attempt == 0:
            # Try sorting by weight (ascending)
            shuffled_stabs = sorted(stabilizers, key=lambda s: len(s.replace('I', '')))
        elif attempt == 1:
            # Try sorting by weight (descending)
            shuffled_stabs = sorted(stabilizers, key=lambda s: len(s.replace('I', '')), reverse=True)
        else:
            shuffled_indices = list(range(len(stabilizers)))
            random.shuffle(shuffled_indices)
            shuffled_stabs = [stabilizers[i] for i in shuffled_indices]
        
        try:
            tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in shuffled_stabs], allow_underconstrained=True)
            circ = tableau.to_circuit()
            
            cx = count_cx(circ)
            
            if cx < best_cx:
                print(f"Found better circuit! Attempt {attempt}: CX={cx}")
                best_cx = cx
                best_circuit = circ
                
                # Verify
                p, t = check_stabilizers(circ, stabilizers)
                if p == t:
                    with open("best_candidate.stim", "w") as f:
                        f.write(str(circ))
                    print("Saved to best_candidate.stim")
                else:
                    best_cx = 257 # Revert if failed (unlikely)
        
        except Exception as e:
            continue

    if best_circuit is not None:
        print(f"Best CX found: {best_cx}")
    else:
        print("No improvement found via reordering.")


if __name__ == "__main__":
    solve()
