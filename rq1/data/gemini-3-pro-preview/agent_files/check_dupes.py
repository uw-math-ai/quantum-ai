def find_duplicates():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_161_fixed.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
        
    seen = {}
    duplicates = []
    for i, line in enumerate(lines):
        if line in seen:
            duplicates.append((seen[line], i, line))
        else:
            seen[line] = i
            
    print(f"Found {len(duplicates)} duplicates.")
    for i, j, line in duplicates:
        print(f"Line {j} is duplicate of {i}: {line[:20]}...")

if __name__ == "__main__":
    find_duplicates()
