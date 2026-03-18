import stim
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
    # Create tableau
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    # Synthesize using Gaussian elimination
    circuit = tableau.to_circuit(method="elimination")
    return circuit

def main():
    try:
        with open("data/baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        base_cx, base_vol = get_metrics(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        
        stabilizers = load_stabilizers("data/stabilizers_fixed_v2.txt")
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        synthesized = synthesize_circuit(stabilizers)
        syn_cx, syn_vol = get_metrics(synthesized)
        print(f"Synthesized: CX={syn_cx}, Vol={syn_vol}")
        
        if syn_cx < base_cx or (syn_cx == base_cx and syn_vol < base_vol):
            print("Synthesized circuit is better!")
            with open("data/optimized.stim", "w") as f:
                f.write(str(synthesized))
        else:
            print("Synthesized circuit is NOT better.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
