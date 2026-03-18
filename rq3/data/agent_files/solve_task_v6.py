import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            # Check for targets_copy method or targets property
            if hasattr(instruction, "targets_copy"):
                 targets = instruction.targets_copy()
            else:
                 # Fallback for very old versions, though unlikely
                 targets = instruction.targets
            count += len(targets) // 2
    return count

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        # Filter empty lines and comments
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return lines

def main():
    # Load baseline
    try:
        baseline = stim.Circuit.from_file("baseline_task_v7.stim")
        print(f"Baseline CX count: {count_cx(baseline)}")
        print(f"Baseline instructions: {len(baseline)}")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    # Load stabilizers
    stabilizers = load_stabilizers("stabilizers_task_v2.txt")
    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Try synthesis
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        # Synthesize
        circuit = tableau.to_circuit(method="elimination")
        print(f"Synthesized Circuit CX count: {count_cx(circuit)}")
        
        # Write to file
        with open("candidate_circuit.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error during synthesis: {e}")

if __name__ == "__main__":
    main()
