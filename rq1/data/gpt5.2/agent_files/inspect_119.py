def inspect_aberrant():
    filename = r'data\gemini-3-pro-preview\agent_files\stabilizers_119.txt'
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print("Index | Length | Content")
    print("-" * 30)
    for i, line in enumerate(lines):
        if len(line) != 119:
            print(f"{i:5d} | {len(line):6d} | {line}")

if __name__ == "__main__":
    inspect_aberrant()
