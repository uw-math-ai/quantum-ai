import stim
import sys

def check():
    try:
        with open("stabilizers_175.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("stabilizers_175.txt not found")
        return

    print(f"Number of stabilizers: {len(stabilizers)}")
    if len(stabilizers) == 0:
        return

    n = len(stabilizers[0])
    print(f"Number of qubits: {n}")
    
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
                if len(anticommuting_pairs) < 10:
                    print(f"Anticommuting pair: {i} ({stabilizers[i]}) and {j} ({stabilizers[j]})")

    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
    else:
        print("All stabilizers commute.")

if __name__ == "__main__":
    check()
