import stim

def check_baseline_signs():
    # Load baseline
    with open("baseline_current.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    # Load target stabilizers (Pauli strings only)
    with open("target_stabilizers_v10.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = [stim.PauliString(l) for l in lines]
    
    # Simulate baseline
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    # Check expectations
    wrong_signs = []
    for i, stab in enumerate(stabilizers):
        expectation = sim.peek_observable_expectation(stab)
        if expectation == -1:
            wrong_signs.append(i)
            print(f"Stabilizer {i} has expectation -1: {stab}")
        elif expectation == 0:
            print(f"Stabilizer {i} has expectation 0 (undefined): {stab}")
    
    if not wrong_signs:
        print("All stabilizers have +1 expectation.")
    else:
        print(f"Found {len(wrong_signs)} stabilizers with -1 expectation.")
        # Save the correct stabilizers (with signs) to a new file
        with open("target_stabilizers_corrected.txt", "w") as f:
            for i, stab in enumerate(stabilizers):
                if i in wrong_signs:
                    f.write("-" + str(stab) + "\n")
                else:
                    f.write(str(stab) + "\n")

if __name__ == "__main__":
    check_baseline_signs()
