def main():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\target_stabilizers.txt", 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    s28 = lines[28]
    s96 = lines[96]
    
    print(f"Index 28: {s28}")
    print(f"Index 96: {s96}")
    
    # Check anticommutation manually
    # Anticommute if odd number of different non-identity Paulis?
    # X and Z anticommute. X and Y anticommute. Y and Z anticommute.
    # Same Pauli commutes. I commutes with everything.
    
    anticommutes = 0
    for i, (c1, c2) in enumerate(zip(s28, s96)):
        if c1 == 'I' or c2 == 'I':
            continue
        if c1 != c2:
            anticommutes += 1
            print(f"Pos {i}: {c1} vs {c2}")
            
    print(f"Anticommutes count: {anticommutes}")
    if anticommutes % 2 == 1:
        print("They ANTICOMMUTE.")
    else:
        print("They COMMUTE.")

if __name__ == "__main__":
    main()
