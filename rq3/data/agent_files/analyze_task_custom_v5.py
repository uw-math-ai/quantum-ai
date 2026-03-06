import stim
import sys

def count_metrics(circuit):
    cx = 0
    vol = 0
    volume_gates = ["CX", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z"]
    for op in circuit:
        if op.name == "CX":
            cx += len(op.targets_copy()) // 2
        
        if op.name in volume_gates:
            if op.name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
                vol += len(op.targets_copy()) // 2
            else:
                vol += len(op.targets_copy())
    return cx, vol

def analyze():
    print("Analyzing baseline...")
    try:
        baseline = stim.Circuit.from_file("baseline_task_v4.stim")
        cx_count, volume = count_metrics(baseline)
        print(f"Baseline Metrics: CX={cx_count}, Volume={volume}")

        print("Loading stabilizers...")
        with open("stabilizers_task_v4.txt", "r") as f:
            stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]
        
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Verify baseline preserves stabilizers
        print("Verifying baseline preservation...")
        tableau = stim.TableauSimulator()
        tableau.do(baseline)
        
        preserved = 0
        for stab in stabilizers:
            p = stim.PauliString(stab)
            if tableau.peek_observable_expectation(p) == 1:
                preserved += 1
        
        print(f"Baseline preserved {preserved}/{len(stabilizers)} stabilizers.")
        
        # Synthesize from stabilizers
        print("Synthesizing from stabilizers...")
        try:
            stab_objs = [stim.PauliString(s) for s in stabilizers]
            # Use both allow_underconstrained and allow_redundant
            synth_tableau = stim.Tableau.from_stabilizers(stab_objs, allow_underconstrained=True, allow_redundant=True)
            synth_circuit = synth_tableau.to_circuit()
            
            synth_cx, synth_volume = count_metrics(synth_circuit)
            print(f"Synthesized Metrics: CX={synth_cx}, Volume={synth_volume}")
            
            # Check validity of synthesized circuit
            print("Verifying candidate preservation...")
            tableau_cand = stim.TableauSimulator()
            tableau_cand.do(synth_circuit)
            preserved_cand = 0
            for stab in stabilizers:
                p = stim.PauliString(stab)
                if tableau_cand.peek_observable_expectation(p) == 1:
                    preserved_cand += 1
            
            print(f"Candidate preserved {preserved_cand}/{len(stabilizers)} stabilizers.")
            
            is_valid = (preserved_cand == len(stabilizers))
            
            # Check if better
            is_better = False
            if synth_cx < cx_count:
                is_better = True
            elif synth_cx == cx_count and synth_volume < volume:
                is_better = True
            
            print(f"Better: {is_better} (Valid: {is_valid})")

            with open("candidate.stim", "w") as f:
                f.write(str(synth_circuit))
            print("Candidate saved to candidate.stim")
            
        except Exception as e:
            print(f"Synthesis failed: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()
