import stim
import sys
import random
import heapq

def count_metrics(circuit):
    cx = 0
    vol = 0
    # Depth is harder, we'll skip for now or use approximate
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CZ"]:
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif instr.name in ["SWAP"]:
            # SWAP is 3 CX
            cx += 3 * (len(instr.targets_copy()) // 2)
            vol += 3 * (len(instr.targets_copy()) // 2)
        else:
            # Single qubit gates
            vol += len(instr.targets_copy())
    return cx, vol

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    for s in stabilizers:
        if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
            return False
    return True

def optimize_by_resynthesis(baseline_circuit, stabilizers):
    # Method 1: Direct Tableau Synthesis
    tableau = stim.Tableau.from_circuit(baseline_circuit)
    
    # Try different synthesis methods if available? 
    # stim currently only has one main one via to_circuit()
    # But we can try to reorder the tableau stabilizers (rows) or qubits (cols) before synthesis?
    # Reordering rows (stabilizers) doesn't change the state.
    # Reordering columns (qubits) does.
    
    # Let's try standard synthesis first
    cand1 = tableau.to_circuit()
    
    return [cand1]

def main():
    # Load
    with open("my_baseline.stim", "r") as f:
        base_text = f.read()
    baseline = stim.Circuit(base_text)
    
    with open("my_stabilizers.txt", "r") as f:
        stabs = [l.strip() for l in f if l.strip()]
        
    base_cx, base_vol = count_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    # Verify baseline first
    if not check_stabilizers(baseline, stabs):
        print("WARNING: Baseline does not preserve stabilizers!")
        
    candidates = optimize_by_resynthesis(baseline, stabs)
    
    best_cand = None
    best_metrics = (base_cx, base_vol)
    
    for i, cand in enumerate(candidates):
        cx, vol = count_metrics(cand)
        print(f"Candidate {i}: CX={cx}, Vol={vol}")
        
        # Check correctness
        if check_stabilizers(cand, stabs):
            if (cx < best_metrics[0]) or (cx == best_metrics[0] and vol < best_metrics[1]):
                print("  -> New Best!")
                best_metrics = (cx, vol)
                best_cand = cand
            else:
                print("  -> Not better.")
        else:
            print("  -> Invalid (stabilizers failed).")
            
    if best_cand:
        with open("best_candidate.stim", "w") as f:
            f.write(str(best_cand))
        print("Saved best_candidate.stim")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    main()
