import stim
import sys
import random

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            # stim counts gates by targets. CX has 2 targets per gate.
            count += len(instr.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name not in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK"]:
            targets = instr.targets_copy()
            if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
                 count += len(targets)
            else:
                 count += len(targets)
    return count

def main():
    baseline_path = "data/agent_files/baseline.stim"
    stabilizers_path = "data/agent_files/target_stabilizers_fixed.txt"
    
    print(f"Loading baseline from {baseline_path}...")
    with open(baseline_path, 'r') as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    baseline_cx = count_cx(baseline)
    baseline_vol = count_volume(baseline)
    print(f"Baseline CX count: {baseline_cx}")
    print(f"Baseline Volume: {baseline_vol}")
    
    print(f"Loading stabilizers from {stabilizers_path}...")
    with open(stabilizers_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Check if lines are valid
    stabilizers = []
    for i, line in enumerate(lines):
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line {i}: {line} -> {e}")
            return

    num_qubits = len(stabilizers[0])
    print(f"Number of stabilizers: {len(stabilizers)}")
    print(f"Number of qubits: {num_qubits}")

    best_cx = baseline_cx
    best_vol = baseline_vol
    best_circuit = baseline
    found_better = False

    # Try original order
    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        synth_circuit = t.to_circuit()
        cx = count_cx(synth_circuit)
        vol = count_volume(synth_circuit)
        print(f"Original order: CX={cx}, Vol={vol}")
        if cx < best_cx or (cx == best_cx and vol < best_vol):
            best_cx = cx
            best_vol = vol
            best_circuit = synth_circuit
            found_better = True
            print("  -> New best!")
    except Exception as e:
        print(f"Original synthesis failed: {e}")

    # Try sorting by weight (length of Pauli string non-identities)
    try:
        # stim.PauliString doesn't have .weight, we calculate it
        # Iterate over PauliString to count non-identity
        # Actually len(ps) is number of qubits. We need weight.
        # But we can't iterate easily.
        # We can convert to string and count non-Is.
        sorted_stabilizers = sorted(stabilizers, key=lambda s: str(s).replace('_', 'I').replace('I', '').count('X') + str(s).replace('_', 'I').replace('I', '').count('Y') + str(s).replace('_', 'I').replace('I', '').count('Z'))
        t = stim.Tableau.from_stabilizers(sorted_stabilizers, allow_underconstrained=True)
        synth_circuit = t.to_circuit()
        cx = count_cx(synth_circuit)
        vol = count_volume(synth_circuit)
        print(f"Sorted by weight: CX={cx}, Vol={vol}")
        if cx < best_cx or (cx == best_cx and vol < best_vol):
            best_cx = cx
            best_vol = vol
            best_circuit = synth_circuit
            found_better = True
            print("  -> New best!")
    except Exception as e:
        print(f"Sorted synthesis failed: {e}")
        import traceback
        traceback.print_exc()

    # Try random shuffles
    print("Trying 1000 random shuffles...")
    for i in range(1000):
        try:
            shuffled = stabilizers.copy()
            random.shuffle(shuffled)
            t = stim.Tableau.from_stabilizers(shuffled, allow_underconstrained=True)
            synth_circuit = t.to_circuit()
            cx = count_cx(synth_circuit)
            vol = count_volume(synth_circuit)
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                best_cx = cx
                best_vol = vol
                best_circuit = synth_circuit
                found_better = True
                print(f"  -> New best at shuffle {i}: CX={cx}, Vol={vol}")
        except Exception as e:
            pass # ignore failures

    print(f"Final best: CX={best_cx}, Vol={best_vol}")
    
    if found_better:
         print("Found a better circuit!")
         with open("data/agent_files/best_candidate.stim", "w") as f:
            f.write(str(best_circuit))
    else:
         print("Did not find a better circuit.")

if __name__ == "__main__":
    main()
