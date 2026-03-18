import stim
import sys

def get_metrics(circuit):
    cx = 0
    vol = 0
    depth = 0
    # Note: depth calculation in stim is not trivial without flattening/dag, 
    # but we can use circuit.num_ticks or approximate.
    # The prompt says "depth" as tertiary.
    # We will trust our own counting for CX and Volume.
    
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            n = len(instruction.targets) // 2
            cx += n
            vol += n
        elif instruction.name in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "CZ", "CY", "SWAP", "ISWAP"]:
             # Volume includes all 1q and 2q gates. 
             # CX is already added.
             # Check if it's a gate.
             if instruction.name in ["CZ", "CY", "SWAP", "ISWAP"]:
                 vol += len(instruction.targets) // 2
             else:
                 vol += len(instruction.targets)
    
    return cx, vol

def main():
    try:
        with open(r"data\baseline.stim", "r") as f:
            content = f.read()
        
        c = stim.Circuit(content)
        cx, vol = get_metrics(c)
        print(f"Baseline: CX={cx}, Volume={vol}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
