import stim
import sys

def check_commutativity(stabilizers):
    num_stabs = len(stabilizers)
    anticommuting_pairs = []
    
    # Convert to stim.PauliString for easier handling
    pauli_stabs = [stim.PauliString(s) for s in stabilizers]
    
    for i in range(num_stabs):
        for j in range(i + 1, num_stabs):
            if not pauli_stabs[i].commutes(pauli_stabs[j]):
                anticommuting_pairs.append((i, j))
                
    return anticommuting_pairs

def main():
    with open('stabilizers_36_latest.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Check string length
    lengths = [len(s) for s in stabilizers]
    if len(set(lengths)) != 1:
        print(f"Error: Stabilizers have different lengths: {set(lengths)}")
        return
    print(f"All stabilizers have length {lengths[0]}.")
    
    anticommuting = check_commutativity(stabilizers)
    
    if not anticommuting:
        print("All stabilizers commute.")
    else:
        print(f"Found {len(anticommuting)} anticommuting pairs.")
        for i, j in anticommuting[:10]:
            print(f"  {i} and {j} anticommute")
            print(f"  {stabilizers[i]}")
            print(f"  {stabilizers[j]}")
        if len(anticommuting) > 10:
            print("  ...")

if __name__ == "__main__":
    main()
