import stim
import sys

def print_candidate(circuit_path):
    with open(circuit_path, "r") as f:
        c = stim.Circuit(f.read())
    
    # Iterate and print
    for op in c:
        if op.name == "CZ":
            targets = op.targets_copy()
            # Print in pairs
            for i in range(0, len(targets), 2):
                t1 = targets[i].value
                t2 = targets[i+1].value
                print(f"CZ {t1} {t2}")
        elif op.name == "TICK":
            print("TICK")
        elif len(op.targets_copy()) > 10:
             # Split long instructions (single qubit gates)
             name = op.name
             targets = op.targets_copy()
             for t in targets:
                 print(f"{name} {t.value}")
        else:
            print(op)

if __name__ == "__main__":
    print_candidate(sys.argv[1])
