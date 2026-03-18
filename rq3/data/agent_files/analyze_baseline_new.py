
import stim
import sys

def main():
    try:
        with open("current_baseline.stim", "r") as f:
            circuit = stim.Circuit(f.read())
            
        print(f"Num qubits: {circuit.num_qubits}")
        
        cx_count = 0
        volume = 0
        depth = 0 # Not easy to calculate exactly without full DAG, but we can approximate or use stim's internal tools if available, or just ignore for now as it is tertiary.
        
        for op in circuit:
            if op.name == "CX":
                cx_count += len(op.targets_copy()) // 2
                volume += len(op.targets_copy()) // 2
            elif op.name in ["H", "S", "X", "Y", "Z", "I"]:
                 volume += len(op.targets_copy())
            else:
                 volume += len(op.targets_copy()) # Generic volume count

        print(f"Refined CX count: {cx_count}")
        print(f"Refined Volume: {volume}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
