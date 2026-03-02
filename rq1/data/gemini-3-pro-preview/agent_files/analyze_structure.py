import stim

def analyze_block_structure():
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Identify blocks by pattern
    # We can just check the first non-I character or the string itself
    # But let's look at the lengths
    for i, line in enumerate(lines):
        if len(line) != 153:
            print(f"Line {i} has length {len(line)}!")
        
    # Let's count blocks
    # We can group by some similarity metric or just look at them
    pass

if __name__ == "__main__":
    analyze_block_structure()
