import stim
import random
import sys

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            n = len(instruction.targets_copy()) // 2
            cx += n
            vol += n
        elif instruction.name in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "CZ", "CY", "SWAP", "ISWAP"]:
             if instruction.name in ["CZ", "CY", "SWAP", "ISWAP"]:
                 vol += len(instruction.targets_copy()) // 2
             else:
                 vol += len(instruction.targets_copy())
    return cx, vol

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f.readlines()]
    stabilizers = []
    for line in lines:
        if line:
            stabilizers.append(stim.PauliString(line))
    return stabilizers

def synthesize_circuit(stabilizers):
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circuit = tableau.to_circuit(method="elimination")
    return circuit

def main():
    stabilizers = load_stabilizers("data/stabilizers_fixed_v2.txt")
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Baseline metrics
    # We know baseline is 1579 CX
    best_cx = 1579
    best_vol = 1632
    best_circuit = None
    
    # Try shuffling
    for i in range(200):
        random.shuffle(stabilizers)
        circuit = synthesize_circuit(stabilizers)
        cx, vol = get_metrics(circuit)
        
        if cx < best_cx or (cx == best_cx and vol < best_vol):
            print(f"Found better! Iter {i}: CX={cx}, Vol={vol}")
            best_cx = cx
            best_vol = vol
            best_circuit = circuit
            # Save immediately
            with open("data/optimized.stim", "w") as f:
                f.write(str(circuit))
        
        if i % 50 == 0:
            print(f"Iter {i}: Best CX={best_cx}")

    if best_circuit:
        print("Optimization successful.")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    main()
