import stim
import sys

def analyze():
    print("Analyzing baseline...")
    try:
        baseline = stim.Circuit.from_file("baseline_task_v4.stim")
        print(f"Baseline loaded. Gates: {len(baseline)}")
        cx_count = sum(1 for op in baseline if op.name == "CX")
        print(f"Baseline CX count: {cx_count}")
        
        # Calculate volume for baseline
        volume_gates = ["CX", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z"]
        volume = sum(1 for op in baseline if op.name in volume_gates)
        print(f"Baseline Volume: {volume}")

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
        
        if preserved != len(stabilizers):
            print("WARNING: Baseline does NOT preserve all stabilizers!")

        # Synthesize from stabilizers
        print("Synthesizing from stabilizers...")
        try:
            stab_objs = [stim.PauliString(s) for s in stabilizers]
            synth_tableau = stim.Tableau.from_stabilizers(stab_objs, allow_underconstrained=True)
            synth_circuit = synth_tableau.to_circuit()
            
            synth_cx = sum(1 for op in synth_circuit if op.name == "CX")
            synth_volume = sum(1 for op in synth_circuit if op.name in volume_gates)
            print(f"Synthesized CX count: {synth_cx}")
            print(f"Synthesized Volume: {synth_volume}")
            
            # Check if better
            is_better = False
            if synth_cx < cx_count:
                is_better = True
            elif synth_cx == cx_count and synth_volume < volume:
                is_better = True
            
            if is_better:
                print("Synthesized circuit is better!")
                with open("candidate.stim", "w") as f:
                    f.write(str(synth_circuit))
                print("Candidate saved to candidate.stim")
            else:
                print("Synthesized circuit is NOT better.")
                # We can still save it to check if it's valid
                with open("candidate.stim", "w") as f:
                    f.write(str(synth_circuit))
            
        except Exception as e:
            print(f"Synthesis failed: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()
