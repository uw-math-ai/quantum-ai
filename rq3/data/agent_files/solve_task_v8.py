import stim
import sys
import random

def count_metrics(circuit):
    cx = 0
    volume = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
             if hasattr(instruction, "targets_copy"):
                 targets = instruction.targets_copy()
             else:
                 targets = instruction.targets
             n = len(targets) // 2
             cx += n
             volume += n
        elif instruction.name in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"]:
             if hasattr(instruction, "targets_copy"):
                 targets = instruction.targets_copy()
             else:
                 targets = instruction.targets
             volume += len(targets)
        # depth is harder to count accurately without simulation, but we focus on cx/volume
    return cx, volume

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return lines

def main():
    # Load stabilizers
    stabilizers = load_stabilizers("stabilizers_task_v7.txt")
    print(f"Loaded {len(stabilizers)} stabilizers.")

    best_cx = 999999
    best_vol = 999999
    best_circuit = None
    best_name = ""

    # Define strategies
    # Sort by first non-I index
    def sort_first(s):
        return sorted(s, key=lambda x: next((i for i, c in enumerate(x) if c in 'XYZ'), 999))
    
    # Sort by last non-I index
    def sort_last(s):
        return sorted(s, key=lambda x: -next((i for i, c in enumerate(reversed(x)) if c in 'XYZ'), 999))

    # Sort by weight (number of non-I)
    def sort_weight(s):
        return sorted(s, key=lambda x: sum(1 for c in x if c in 'XYZ'))

    # Sort by weight descending
    def sort_weight_desc(s):
        return sorted(s, key=lambda x: -sum(1 for c in x if c in 'XYZ'))
    
    strategies = [
        ("original", lambda s: s),
        ("sorted_first", sort_first),
        ("sorted_last", sort_last),
        ("sorted_weight", sort_weight),
        ("sorted_weight_desc", sort_weight_desc),
        ("reverse", lambda s: list(reversed(s))),
    ]
    
    # Add random shuffles
    for i in range(100):
        strategies.append((f"shuffle_{i}", lambda s: random.sample(s, len(s))))

    for name, strategy in strategies:
        try:
            current_stabilizers = strategy(stabilizers)
            tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in current_stabilizers], allow_underconstrained=True, allow_redundant=True)
            
            circuit = tableau.to_circuit(method="elimination")
            cx, vol = count_metrics(circuit)
            
            # Check improvement
            is_better = False
            if cx < best_cx:
                is_better = True
            elif cx == best_cx and vol < best_vol:
                is_better = True
            
            if is_better:
                best_cx = cx
                best_vol = vol
                best_circuit = circuit
                best_name = name
                print(f"New best: {cx} CX, {vol} Vol using {name}")

        except Exception as e:
            # print(f"Strategy {name} failed: {e}")
            pass

    print(f"Final Best: {best_cx} CX, {best_vol} Vol (Method: {best_name})")
    
    if best_circuit:
        with open("candidate_circuit.stim", "w") as f:
            f.write(str(best_circuit))

if __name__ == "__main__":
    main()
