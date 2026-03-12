import stim

def main():
    filename = "target_stabilizers.txt"
    try:
        with open(filename, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        stabilizers = [stim.PauliString(l) for l in lines]
        print(f"Loaded {len(stabilizers)} stabilizers from {filename}")
        
        # Check consistency
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        print("Stabilizers are consistent (commute).")
        
        # Check if baseline preserves them
        with open("baseline_task.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        
        sim = stim.TableauSimulator()
        sim.do(baseline)
        
        failed = []
        for i, s in enumerate(stabilizers):
            if sim.peek_observable_expectation(s) != 1:
                failed.append(i)
        
        if failed:
            print(f"Baseline fails to preserve {len(failed)} stabilizers: {failed}")
        else:
            print("Baseline preserves all stabilizers in target_stabilizers.txt")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
