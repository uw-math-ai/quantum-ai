import stim
import sys

# Target stabilizers from prompt
target_stabilizers_str = [
    "IIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX", "IXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXX", "XXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXI", "IIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZ", "IZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ", "ZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZI", "XXIXIIIZZIZIIIZZIZIIIXXIXIIIIIIIIII", "IIIIIIIXXIXIIIZZIZIIIZZIZIIIXXIXIII", "XXIXIIIIIIIIIIXXIXIIIZZIZIIIZZIZIII", "ZZIZIIIXXIXIIIIIIIIIIXXIXIIIZZIZIII"
]

baseline_str = """
CX 30 0 0 30 30 0
H 0 3 13 16 21
CX 0 3 0 13 0 16 0 21 0 25 0 33
H 10 32
CX 10 0 32 0 25 1 1 25 25 1 1 20 1 33
H 5
CX 5 1 10 1 32 1 10 2 2 10 10 2 2 5 2 15 2 33
H 30
CX 30 2 20 3 3 20 20 3 3 33 5 3 15 3 32 3 30 4 4 30 30 4 4 5 5 15 5 33 15 6 6 15 15 6 6 33 33 7 7 33 33 7
H 7 15 24 29 34
CX 7 13 7 15 7 20 7 24 7 26 7 29 7 34
H 11 31
CX 11 7 31 7 15 8 8 15 15 8
H 21
CX 8 21 8 26 11 8 31 8 11 9 9 11 11 9
H 16
CX 9 16 9 21 9 26
H 25
CX 25 9 21 10 10 21 21 10 16 10 31 10 25 11 11 25 25 11 11 26 26 12 12 26 26 12 12 16 16 13 13 16 16 13 32 14 14 32 32 14
S 31 34
H 30 32 33
CX 14 24 14 27 14 29 14 30 14 31 14 32 14 33 14 34
H 26
CX 26 14 26 15 15 26 26 15
H 21
CX 15 21 15 22 33 15 21 16 16 21 21 16 16 17 16 27 33 17 17 33 33 17 17 27 33 18 18 33 33 18 22 18 27 19 19 27 27 19 19 22 22 20 20 22 22 20
H 26 31
CX 21 22 21 26 21 28 21 31 26 22 22 26 26 22 22 23 22 28 22 31 26 23 23 26 26 23 23 28 23 33 31 24 24 31 31 24
S 24
H 24
S 24
CX 24 26
H 30 32
CX 30 24 32 24 34 24 33 25 25 33 33 25 26 25 30 25 32 25 34 25 28 26 26 28 28 26 26 28 28 27 27 28 28 27 30 27 32 27 34 27 32 28 28 32 32 28
H 28 29 30 33
CX 28 29 28 30 28 33 33 29 29 33 33 29
H 31 34
CX 29 31 29 33 29 34 30 32 30 33 30 34
S 34
H 34
CX 33 31 34 31 33 32 34 32
S 34
H 24 25 27
S 24 24 25 25 27 27
H 24 25 27
S 0 0 2 2 4 4 7 7 9 9 11 11 22 22 23 23 27 27
"""

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name == "CX":
            count += len(op.targets_copy()) // 2
    return count

def count_volume(circuit):
    # Volume is total gate count in volume gate set
    # We'll count every target as a gate application
    count = 0
    for op in circuit:
        if op.name in ["CX", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z"]: # Add others if needed
             count += len(op.targets_copy()) # For 2Q gates, it counts 2. For 1Q, 1.
             # Wait, volume usually counts 'gates'. A CX is 1 gate? Or 2?
             # Standard definition: Number of operations in the volume.
             # If CX 0 1 is 1 gate, then len/2.
             if len(op.targets_copy()) > 1:
                 count += len(op.targets_copy()) // 2
             else:
                 count += len(op.targets_copy())
    return count

def main():
    try:
        baseline = stim.Circuit(baseline_str)
        base_cx = count_cx(baseline)
        print(f"Baseline CX: {base_cx}")

        stabilizers = [stim.PauliString(s) for s in target_stabilizers_str]
        
        # Verify baseline validity first (to ensure stabs are correct)
        sim = stim.TableauSimulator()
        sim.do_circuit(baseline)
        valid_base = True
        for s in stabilizers:
            if sim.peek_observable_expectation(s) != 1:
                valid_base = False
                break
        print(f"Baseline valid: {valid_base}")

        # Resynthesize
        print("Resynthesizing...")
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        # Method 1: Elimination
        cand1 = tableau.to_circuit("elimination")
        cx1 = count_cx(cand1)
        print(f"Method 'elimination' CX: {cx1}")
        
        # Method 2: Graph state (if available/better)
        # Note: stim.Tableau.to_circuit doesn't take 'graph_state' in all versions.
        # But let's stick to what we have.
        
        # Write best candidate
        if cx1 < base_cx:
            with open("candidate.stim", "w") as f:
                f.write(str(cand1))
            print("Wrote candidate.stim")
        else:
            print("No improvement.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
