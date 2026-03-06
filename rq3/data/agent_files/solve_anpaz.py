import stim

def solve():
    print("Analyzing...")
    try:
        with open("prompt_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        stabilizers = []
        for l in lines:
            if "," in l:
                # remove index, format: "0, II..."
                parts = l.split(",")
                stabilizers.append(stim.PauliString(parts[-1].strip()))
            else:
                stabilizers.append(stim.PauliString(l))
        
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Load baseline
        with open("prompt_baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        
        base_cx = 0
        base_vol = 0
        for instr in baseline:
            if instr.name == "CX":
                n = len(instr.targets_copy()) // 2
                base_cx += n
                base_vol += n
            elif instr.name in ["H", "S", "X", "Y", "Z", "I"]:
                base_vol += len(instr.targets_copy())
            else:
                # Count other gates roughly
                base_vol += len(instr.targets_copy())

        print(f"Baseline CX: {base_cx}")
        print(f"Baseline Vol: {base_vol}")
        
        # Try synthesis
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        # Method 1: Standard synthesis
        circ1 = tableau.to_circuit()
        c1_cx = 0
        for instr in circ1:
            if instr.name == "CX":
                c1_cx += len(instr.targets_copy()) // 2
        
        print(f"Standard Synthesis CX: {c1_cx}")
        
        # Method 2: Graph State (manual)
        # This is complex to implement from scratch.
        # But maybe the standard synthesis IS good enough?
        
        if c1_cx < base_cx:
            print("Standard synthesis is better!")
            with open("candidate.stim", "w") as f:
                f.write(str(circ1))
        else:
            print("Standard synthesis is worse or equal.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
