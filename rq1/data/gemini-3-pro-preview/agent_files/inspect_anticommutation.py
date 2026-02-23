def inspect_anticommutation(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    num_qubits = len(lines[0])
    
    pairs = []
    for i, s1 in enumerate(lines):
        for j, s2 in enumerate(lines):
            if i >= j: continue
            
            comm = 0
            overlap = []
            for k in range(num_qubits):
                p1 = s1[k]
                p2 = s2[k]
                if p1 != 'I' and p2 != 'I':
                    if p1 != p2:
                        comm += 1
                        overlap.append((k, p1, p2))
            
            if comm % 2 == 1:
                pairs.append((i, j, overlap))

    print(f"Found {len(pairs)} anticommuting pairs.")
    
    conflict_counts = {}
    for i, j, _ in pairs:
        conflict_counts[i] = conflict_counts.get(i, 0) + 1
        conflict_counts[j] = conflict_counts.get(j, 0) + 1
        
    sorted_conflicts = sorted(conflict_counts.items(), key=lambda x: x[1], reverse=True)
    print("Stabilizers with most conflicts:")
    for idx, count in sorted_conflicts:
        print(f"Stabilizer {idx}: {count} conflicts")
        print(lines[idx])
        
    print("\nDetailed pairs:")
    for i, j, overlap in pairs:
        print(f"({i}, {j}): Overlap at {overlap}")

inspect_anticommutation(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_114.txt')
