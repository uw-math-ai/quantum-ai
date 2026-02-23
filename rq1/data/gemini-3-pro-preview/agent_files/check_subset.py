def check_subset_commutation(filename, remove_indices):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    num_qubits = len(lines[0])
    
    subset = []
    for i in range(len(lines)):
        if i not in remove_indices:
            subset.append(lines[i])
            
    # Check for anticommutation in subset
    count = 0
    for i in range(len(subset)):
        for j in range(i + 1, len(subset)):
            s1 = subset[i]
            s2 = subset[j]
            comm = 0
            for k in range(num_qubits):
                if s1[k] != 'I' and s2[k] != 'I' and s1[k] != s2[k]:
                    comm += 1
            if comm % 2 == 1:
                count += 1
                
    print(f"Removed {len(remove_indices)} stabilizers: {remove_indices}")
    print(f"Remaining conflicts: {count}")

check_subset_commutation(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_114.txt', [38, 92])
