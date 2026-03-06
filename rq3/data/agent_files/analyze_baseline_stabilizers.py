import stim
import sys

def main():
    try:
        # Load targets
        with open("current_task_stabilizers.txt", "r") as f:
            target_lines = [l.strip() for l in f if l.strip()]
        targets = [stim.PauliString(l) for l in target_lines]
        print(f"Loaded {len(targets)} target stabilizers.")

        # Check consistency of targets
        print("Checking target consistency...")
        consistent = True
        for i in range(len(targets)):
            for j in range(i + 1, len(targets)):
                if stim.PauliString(targets[i]).commutes(stim.PauliString(targets[j])) == False:
                    print(f"CONFLICT: Target {i} and Target {j} anticommute!")
                    consistent = False
                    if i == 28 and j == 77:
                        print(f"  Target {i}: {targets[i]}")
                        print(f"  Target {j}: {targets[j]}")
                    if not consistent:
                        break
            if not consistent:
                break
        
        if consistent:
            print("Targets are CONSISTENT.")
        else:
            print("Targets are INCONSISTENT.")

        # Load baseline
        with open("current_task_baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        print(f"Loaded baseline with {len(baseline)} instructions.")

        # Check preservation
        sim = stim.TableauSimulator()
        sim.do(baseline)
        
        preserved_count = 0
        failed_indices = []
        for i, t in enumerate(targets):
            if sim.peek_observable_expectation(t) == 1:
                preserved_count += 1
            else:
                failed_indices.append(i)
        
        print(f"Baseline preserves {preserved_count}/{len(targets)} targets.")
        if failed_indices:
            print(f"Failed indices (first 10): {failed_indices[:10]}")

        # Get actual stabilizers of baseline
        # tableau = stim.Tableau.from_circuit(baseline)
        # canon_stabilizers = tableau.to_stabilizers()
        # print(f"Baseline generates {len(canon_stabilizers)} stabilizers.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
