import stim
import sys

def main():
    # Read stabilizers
    with open("my_stabilizers.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = [stim.PauliString(s) for s in lines]
    
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}", file=sys.stderr)
        return

    try:
        candidate = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error synthesizing circuit: {e}", file=sys.stderr)
        return
    
    # Check for RX, RY, R_X, R_Y, R_Z, M, MPP which might be disallowed
    # The allowed gates are usually those in the baseline + standard Clifford gates.
    # The prompt says: "Do NOT introduce measurements, resets, or noise unless they already exist in the baseline"
    # So we must replace resets with initialization if possible, or ensure we don't use them.
    # Since we start from |0>, RX is equivalent to H * R (reset to 0). But R is forbidden if not in baseline.
    # But we assume start from |0>, so R is identity. So RX is just H.
    
    # print(new_circuit) # Stim merges instructions, so we print manually
    
    # We want to print instructions one by one to avoid long lines
    # Also we want to ensure valid Stim format
    
    for instr in candidate:
        name = instr.name
        targets = instr.targets_copy()
        args = instr.gate_args_copy()
        
        if name == "RX":
            # Replace with H
            for t in targets:
                print(f"H {t.value}")
        elif name == "RY":
             # Replace with H S
             for t in targets:
                 print(f"H {t.value}")
                 print(f"S {t.value}")
        elif name == "R" or name == "RZ":
            pass
        elif name == "CZ":
            # Split CZ into pairs
            for i in range(0, len(targets), 2):
                t1 = targets[i].value
                t2 = targets[i+1].value
                print(f"CZ {t1} {t2}")
        elif name == "H" or name == "X" or name == "Y" or name == "Z" or name == "S":
            # Split single qubit gates
            for t in targets:
                print(f"{name} {t.value}")
        elif name == "TICK":
            print("TICK")
        else:
            # Other instructions, print as is
            # We need to format them correctly
            # Assuming simple instructions without args for now, or use str(instr)
            print(str(instr))


if __name__ == "__main__":
    main()
