import stim

def run():
    # Load stabilizers
    with open("stabilizers_task_v10.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = [stim.PauliString(s) for s in lines]
    
    # Try creating a Tableau
    # Note: from_stabilizers creates a tableau T such that T|0> stabilizes the given stabilizers.
    # If underconstrained, it picks arbitrary completions.
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Failed to create tableau: {e}")
        return

    # Synthesize circuit
    # method="elimination" is the standard Gaussian elimination
    circuit = tableau.to_circuit(method="elimination")
    
    # Count CX
    cx_count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            cx_count += len(instr.targets_copy()) // 2
            
    print(f"Synthesized Circuit CX count: {cx_count}")
    
    # Also try graph state synthesis if possible?
    # Stim doesn't have direct graph state synthesis from tableau, but we can check if it's better.
    
    # Let's save this candidate to see if it's better
    with open("candidate_synthesis.stim", "w") as f:
        f.write(str(circuit))

if __name__ == "__main__":
    run()
