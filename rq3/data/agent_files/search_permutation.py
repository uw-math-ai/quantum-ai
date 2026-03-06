import stim
import random
import sys

def count_cx(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        args = instr.gate_args_copy()
        targets = instr.targets_copy()
        if instr.name == "CX":
            n = len(targets) // 2
            cx += n
            vol += n
        elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            n = len(targets) // 2
            vol += n
        else:
            vol += len(targets)
    return cx, vol

def solve():
    print("Loading stabilizers...")
    with open("prompt_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = []
    for l in lines:
        if "," in l:
            parts = l.split(",")
            stabilizers.append(stim.PauliString(parts[-1].strip()))
        else:
            stabilizers.append(stim.PauliString(l))
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Baseline check
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    base_circ = tableau.to_circuit()
    base_cx, base_vol = count_cx(base_circ)
    print(f"Baseline (default order): CX={base_cx}, Vol={base_vol}")
    
    best_cx = base_cx
    best_vol = base_vol
    best_circ = base_circ
    
    # Try shuffling
    for i in range(200):
        random.shuffle(stabilizers)
        try:
            # Note: allow_underconstrained=True is needed if len(stabs) < num_qubits
            # But wait, does shuffling change the set? No.
            # Does it change the tableau synthesis? Yes, pivot selection depends on order.
            t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            c = t.to_circuit()
            cx, vol = count_cx(c)
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"Found better! Iter={i}, CX={cx}, Vol={vol}")
                best_cx = cx
                best_vol = vol
                best_circ = c
                
                # Save immediately
                with open("candidate_improved.stim", "w") as f:
                    f.write(str(best_circ))
            
            if i % 20 == 0:
                print(f"Iter {i}: CX={cx}")
                
        except Exception as e:
            print(f"Error in iter {i}: {e}")
            
    print(f"Best found: CX={best_cx}, Vol={best_vol}")

if __name__ == "__main__":
    solve()
