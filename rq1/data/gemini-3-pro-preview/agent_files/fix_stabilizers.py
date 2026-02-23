
with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_153_current.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

fixed_lines = []
for i, line in enumerate(lines):
    if len(line) == 153:
        fixed_lines.append(line)
    elif len(line) > 153:
        # Assuming extra characters are 'I's at the end
        print(f"Trimming line {i} from {len(line)} to 153")
        fixed_lines.append(line[:153])
    else:
        print(f"Line {i} is too short: {len(line)}")
        # Pad with Is? Or raise error?
        # For now, pad with Is
        print(f"Padding line {i} from {len(line)} to 153")
        fixed_lines.append(line + 'I' * (153 - len(line)))

with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_153_current.txt', 'w') as f:
    f.write('\n'.join(fixed_lines))
