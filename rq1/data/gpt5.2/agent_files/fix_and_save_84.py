import stim

def fix_and_save():
    with open("stabilizers_84_task.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    fixed_lines = []
    for line in lines:
        if len(line) == 86:
            # Check if it fits the pattern by removing 2 chars from end
            # We assume the extra chars are Is at the end.
            new_line = line[:-2]
            fixed_lines.append(new_line)
        else:
            fixed_lines.append(line)
            
    with open("stabilizers_84_fixed.txt", "w") as f:
        for line in fixed_lines:
            f.write(line + "\n")
            
    print(f"Saved {len(fixed_lines)} lines to stabilizers_84_fixed.txt")

if __name__ == "__main__":
    fix_and_save()
