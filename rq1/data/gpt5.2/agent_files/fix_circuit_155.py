import re

def fix_circuit():
    with open("circuit_155.stim", "r") as f:
        content = f.read()
    
    # Remove newlines that break commands?
    # Actually, stim format: COMMAND arg arg arg...
    # Newlines are command separators.
    # If a command is split across lines, it might be an issue if the split happens in the middle of arguments?
    # Stim does NOT support splitting commands across lines unless line continuation is used?
    # Actually, Stim generally requires one command per line.
    
    # Check if lines are broken.
    lines = content.split('\n')
    fixed_lines = []
    current_line = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Heuristic: if a line starts with a digit, it's likely a continuation of the previous line
        if line[0].isdigit():
            if fixed_lines:
                fixed_lines[-1] += " " + line
            else:
                # Should not happen
                print(f"Warning: line starts with digit but no previous line: {line}")
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
            
    fixed_content = "\n".join(fixed_lines)
    
    with open("circuit_155_fixed.stim", "w") as f:
        f.write(fixed_content)

if __name__ == "__main__":
    fix_circuit()
