import stim
import sys
import random

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            count += len(instr.targets_copy()) // 2
    return count

def get_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK"]:
            continue
        n_targets = len(instr.targets_copy())
        if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            count += n_targets // 2  # Count gates, not operations? No, usually volume is total operations.
            # But let's stick to what we used before.
            # Actually, "volume" usually means total gate count.
            # But for 2-qubit gates, it's 1 gate.
            # Let's count operations.
            # Wait, "volume – total gate count in the volume gate set".
            # If I have H 0 1 2, that's 3 gates.
            # If I have CX 0 1 2 3, that's 2 CX gates.
            pass
        else:
            # 1-qubit gates
            # count += n_targets
            pass
    # Re-implement get_volume correctly based on prompt definition
    # "volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)."
    # This implies counting every single-qubit gate and every two-qubit gate.
    # Stim stores "H 0 1 2" as one instruction.
    # We should sum len(targets) for 1-qubit gates, and len(targets)/2 for 2-qubit gates.
    vol = 0
    for instr in circuit:
        if instr.name in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK"]:
            continue
        n = len(instr.targets_copy())
        if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            vol += n // 2
        else:
            vol += n
    return vol

def main():
    # Load stabilizers
    with open("data/agent_files/target_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Load baseline
    with open("data/agent_files/baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    base_cx = count_cx(baseline)
    base_vol = get_volume(baseline)

    print(f"Baseline CX count: {base_cx}")
    print(f"Baseline Volume: {base_vol}")

    # Create Tableau from stabilizers
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    best_cx = base_cx
    best_vol = base_vol
    best_circuit = None
    
    # Try original order first
    # Then try random shuffles
    
    trials = 1000
    for i in range(trials):
        current_stabilizers = list(pauli_stabilizers)
        if i > 0:
            random.shuffle(current_stabilizers)
            
        try:
            tableau = stim.Tableau.from_stabilizers(current_stabilizers, allow_underconstrained=True)
            synthesized = tableau.to_circuit(method="elimination")
            
            syn_cx = count_cx(synthesized)
            syn_vol = get_volume(synthesized)
            
            if syn_cx < best_cx or (syn_cx == best_cx and syn_vol < best_vol):
                print(f"New best found at trial {i}: CX={syn_cx}, Vol={syn_vol}")
                best_cx = syn_cx
                best_vol = syn_vol
                best_circuit = synthesized
                
                with open("data/agent_files/candidate.stim", "w") as f:
                    f.write(str(synthesized))
                    
        except Exception as e:
            # print(f"Error: {e}")
            pass

    if best_circuit is not None:
        print("Found a better circuit!")
    else:
        print("No better circuit found.")

if __name__ == "__main__":
    main()
