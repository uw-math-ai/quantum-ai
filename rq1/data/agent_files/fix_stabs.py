def fix():
    with open('stabilizers_135.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    fixed_lines = []
    for line in lines:
        if len(line) == 137:
            # truncate last 2 chars
            fixed_lines.append(line[:-2])
        else:
            fixed_lines.append(line)

    with open('stabilizers_135.txt', 'w') as f:
        f.write('\n'.join(fixed_lines))
    print("Fixed.")

if __name__ == "__main__":
    fix()
