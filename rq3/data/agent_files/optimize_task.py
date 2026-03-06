
import stim
import sys

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif instr.name in ["H", "S", "SQRT_X", "S_DAG", "SQRT_X_DAG", "X", "Y", "Z", "I", "CY", "CZ", "SWAP"]:
             vol += len(instr.targets_copy())
    return cx, vol

def solve():
    print("Loading data...")
    # Read the file line by line to get raw circuit
    with open("my_baseline.stim", "r") as f:
        baseline_text = f.read()
    
    # Stim circuit parsing
    try:
        baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error parsing baseline: {e}")
        return

    # Stabilizers
    with open("my_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Count baseline metrics
    cx_base, vol_base = 0, 0
    for instr in baseline:
        if instr.name == "CX":
            n = len(instr.targets_copy()) // 2
            cx_base += n
            vol_base += n
        elif instr.name in ["H", "S", "SQRT_X", "S_DAG", "SQRT_X_DAG", "X", "Y", "Z", "I"]:
            vol_base += len(instr.targets_copy())
            
    print(f"Baseline: CX={cx_base}, Vol={vol_base}")

    # Create Tableau from stabilizers
    # Stim 1.13+ supports Tableau.from_stabilizers
    try:
        # Convert strings to PauliStrings
        pauli_stabs = [stim.PauliString(s) for s in stabilizers]
        print(f"Num stabilizers: {len(pauli_stabs)}")
        
        # Check consistency/validity
        # A valid stabilizer group must commute.
        # Stim checks this?
        
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_redundant=True, allow_underconstrained=True)
        # Note: If underconstrained, it picks SOME state. If stabilizers define a unique state, great.
        # The prompt says "Target stabilizers (must all be preserved)". It does not say they form a complete set.
        # But usually for strict improvement, we want to synthesize THE SAME state.
        
        # Synthesize a circuit for this tableau
        # Method: "elimination" (Gaussian elimination)
        # Often produces O(n^2) gates.
        synth_circuit = tableau.to_circuit(method="elimination")
        
        # Count metrics for new circuit
        cx_new, vol_new = 0, 0
        for instr in synth_circuit:
            if instr.name == "CX":
                n = len(instr.targets_copy()) // 2
                cx_new += n
                vol_new += n
            elif instr.name in ["H", "S", "SQRT_X", "S_DAG", "SQRT_X_DAG", "X", "Y", "Z", "I"]:
                vol_new += len(instr.targets_copy())

        print(f"Synthesized (elimination): CX={cx_new}, Vol={vol_new}")

        if (cx_new < cx_base) or (cx_new == cx_base and vol_new < vol_base):
            print("Improvement found via synthesis!")
            with open("candidate_synthesis.stim", "w") as f:
                f.write(str(synth_circuit))
        else:
            print("Synthesis was worse.")

    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    solve()

