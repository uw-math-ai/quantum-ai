with open('target_stabilizers_new_task.txt', 'r') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Num lines: {len(lines)}")
print(f"First line length: {len(lines[0])}")
print(f"First line: {lines[0]}")
