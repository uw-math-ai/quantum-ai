with open("circuit_54_graph_clean.stim", "r") as f:
    lines = f.readlines()
    print(f"Line 2 length: {len(lines[1])}")
    print(f"Last 50 chars of line 2: '{lines[1][-50:].strip()}'")
