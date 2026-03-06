import stim

def check_active_indices():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\target_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    max_index = 0
    active_indices = set()
    for s in stabilizers:
        for i, char in enumerate(s):
            if char in "XYZ":
                active_indices.add(i)
                max_index = max(max_index, i)
    
    print(f"Max active index: {max_index}")
    print(f"Active indices count: {len(active_indices)}")
    print(f"Sorted active indices: {sorted(list(active_indices))}")
    print(f"Last stabilizer: {stabilizers[-1]}")
    print(f"Last stabilizer length: {len(stabilizers[-1])}")

if __name__ == "__main__":
    check_active_indices()
