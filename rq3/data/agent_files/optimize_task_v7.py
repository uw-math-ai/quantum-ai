import stim

def solve():
    # 1. Load baseline
    try:
        baseline = stim.Circuit.from_file("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\data\\agent_files\\baseline.stim")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    # 2. Get the tableau implemented by the baseline
    # The baseline is a unitary circuit (no measurements).
    # We want a circuit that implements the same unitary (stabilizer evolution).
    try:
        tableau = stim.Tableau.from_circuit(baseline)
    except Exception as e:
        print(f"Error computing tableau: {e}")
        return

    # 3. Synthesize a new circuit from the tableau
    # method="elimination" is the standard Gaussian elimination synthesis.
    try:
        new_circuit = tableau.to_circuit(method="elimination")
    except Exception as e:
        print(f"Error synthesizing circuit: {e}")
        return

    # 4. Compare metrics
    def get_metrics(circuit):
        cx = 0
        vol = 0
        depth = 0 # Approximate
        for instruction in circuit:
            if instruction.name == "CX" or instruction.name == "CNOT":
                n = len(instruction.targets_copy()) // 2
                cx += n
                vol += n
            elif instruction.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
                 # This is a rough count, but good enough for relative comparison locally.
                 # The official tool uses 'volume' gate set.
                 # H, S, etc count as 1. CX counts as 1 (or maybe 2? usually 1).
                 # Standard definition of volume usually counts 2-qubit gates and 1-qubit gates.
                 # The prompt says: "volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)."
                 # So just count all gates.
                 n = len(instruction.targets_copy())
                 if instruction.name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
                      # 2 qubit gates. Stim stores targets in a list. For CX it's pairs.
                      # If 2 targets, it's 1 gate.
                      num_gates = n // 2
                      vol += num_gates
                 else:
                      vol += n
        return cx, vol

    base_cx, base_vol = get_metrics(baseline)
    new_cx, new_vol = get_metrics(new_circuit)

    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    print(f"New:      CX={new_cx}, Vol={new_vol}")

    if new_cx < base_cx or (new_cx == base_cx and new_vol < base_vol):
        print("IMPROVEMENT FOUND")
        # Save to file
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\data\\agent_files\\optimized.stim", "w") as f:
            f.write(str(new_circuit))
    else:
        print("No improvement with standard synthesis.")
        # Try a different method?
        # Maybe reverse order?
        # Maybe inverse?
        pass

if __name__ == "__main__":
    solve()
