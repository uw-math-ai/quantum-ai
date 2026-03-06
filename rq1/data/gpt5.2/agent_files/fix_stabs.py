
def fix_stabilizers():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    fixed_lines = []
    for i, line in enumerate(lines):
        if len(line) == 75:
            fixed_lines.append(line)
        elif len(line) == 76:
            # Check if it ends with 'I' and removing it makes sense
            # Or if it starts with 'I' and removing it makes sense
            # Or just blindly remove the last char if it's 'I'
            if line.endswith('I'):
                fixed_lines.append(line[:-1])
            else:
                print(f"Line {i} length 76 but doesn't end with I: {line}")
                fixed_lines.append(line) # Keep it, maybe valid?
        else:
            print(f"Line {i} has weird length {len(line)}")
            fixed_lines.append(line)
            
    with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "w") as f:
        f.write("\n".join(fixed_lines) + "\n")
    print("Fixed stabilizers file.")

if __name__ == "__main__":
    fix_stabilizers()
