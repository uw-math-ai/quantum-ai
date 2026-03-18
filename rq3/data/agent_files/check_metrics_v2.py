import stim
import sys

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        targets = instr.targets_copy()
        if instr.name in ["CX", "CNOT"]:
            cx += len(targets) // 2
            vol += len(targets) // 2
        elif instr.name in ["CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z"]:
             # Volume includes 1-qubit and 2-qubit gates
             # But the prompt definition says: "total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
             # Assuming this means number of operations.
             if instr.name in ["CX", "CY", "CZ"]:
                 vol += len(targets) // 2
             else:
                 vol += len(targets)
    return cx, vol

if __name__ == "__main__":
    circuit_str = sys.stdin.read()
    circuit = stim.Circuit(circuit_str)
    cx, vol = count_metrics(circuit)
    print(f"CX: {cx}, Volume: {vol}")
