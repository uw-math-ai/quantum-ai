with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\target_stabilizers.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

bad_line_index = 61
print(f"Removing line {bad_line_index}: {lines[bad_line_index]}")
del lines[bad_line_index]

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\target_stabilizers.txt", "w") as f:
    for line in lines:
        f.write(line + "\n")
