def check_dupes():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_135.txt", 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    seen = set()
    dupes = []
    for line in lines:
        if line in seen:
            dupes.append(line)
        seen.add(line)
        
    print(f"Total lines: {len(lines)}")
    print(f"Unique lines: {len(seen)}")
    if dupes:
        print("Duplicates found:")
        for d in dupes:
            print(d)
            
if __name__ == "__main__":
    check_dupes()
