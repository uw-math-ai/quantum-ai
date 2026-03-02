import os

def check_lengths():
    filename = r'data\gemini-3-pro-preview\agent_files\stabilizers_119.txt'
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Total lines: {len(lines)}")
    lengths = {}
    for i, line in enumerate(lines):
        L = len(line)
        if L not in lengths:
            lengths[L] = []
        lengths[L].append(i)

    for L in sorted(lengths.keys()):
        print(f"Length {L}: {len(lengths[L])} stabilizers (indices: {lengths[L][:5]}...)")

    # If most are length 119, maybe the others are typos or can be padded/truncated.
    # Let's see which ones deviate.
    
if __name__ == "__main__":
    check_lengths()
