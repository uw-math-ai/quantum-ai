def check_shifts():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_135.txt", 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print("Checking shifts for IIZZIZZ block (lines 55-63 approx)")
    # The block starts with IIZZIZZ...
    # Find the block start
    start_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("IIZZIZZ"):
            start_idx = i
            break
            
    if start_idx == -1:
        print("Block not found")
        return

    for i in range(start_idx, start_idx + 9):
        line = lines[i]
        # find first non-I
        first_non_i = -1
        for j, c in enumerate(line):
            if c != 'I':
                first_non_i = j
                break
        print(f"Line {i+1}: Start index {first_non_i}")

if __name__ == "__main__":
    check_shifts()
