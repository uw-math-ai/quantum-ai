import stim

def check_commutativity():
    with open("stabilizers_161.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))

    print(f"Total stabilizers: {len(stabilizers)}")
    print(f"Number of anticommuting pairs: {len(anticommuting_pairs)}")
    
    conflict_counts = {}
    for i, j in anticommuting_pairs:
        conflict_counts[i] = conflict_counts.get(i, 0) + 1
        conflict_counts[j] = conflict_counts.get(j, 0) + 1

    print("Conflict counts per stabilizer index:")
    for idx in sorted(conflict_counts.keys()):
        print(f"  Index {idx}: {conflict_counts[idx]} conflicts")

if __name__ == "__main__":
    check_commutativity()
