with open('data/gemini-3-pro-preview/agent_files/stabilizers_175_task.txt', 'r') as f:
    lines = [line.strip().replace(',', '') for line in f if line.strip()]

fixed_lines = []
for i, line in enumerate(lines):
    if len(line) < 175:
        print(f"Fixing line {i} (len {len(line)})")
        line = line + 'I' * (175 - len(line))
    fixed_lines.append(line)

with open('data/gemini-3-pro-preview/agent_files/stabilizers_175_task.txt', 'w') as f:
    for line in fixed_lines:
        f.write(line + '\n')

print("Fixed lengths.")
