s92 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIIIIZZIIIIIIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
# Count leading Is.
count = 0
for c in s92:
    if c == 'I':
        count += 1
    else:
        break
print(f"Leading Is: {count}")

with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_114.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

idx = lines.index(s92)
print(f"Index in file: {idx}")
