def fix_lengths():
    with open("stabilizers_119.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    fixed_lines = []
    for i, l in enumerate(lines):
        if len(l) == 119:
            fixed_lines.append(l)
        elif len(l) > 119:
            print(f"Truncating line {i} from {len(l)} to 119")
            fixed_lines.append(l[:119])
        else:
            print(f"Padding line {i} from {len(l)} to 119")
            fixed_lines.append(l + "I" * (119 - len(l)))
            
    with open("stabilizers_119_fixed.txt", "w") as f:
        for l in fixed_lines:
            f.write(l + "\n")
            
    print("Fixed stabilizers saved to stabilizers_119_fixed.txt")

if __name__ == "__main__":
    fix_lengths()
