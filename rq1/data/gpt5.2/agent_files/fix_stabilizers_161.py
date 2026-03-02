
def fix_stabilizers():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v2.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    fixed_lines = []
    for i, line in enumerate(lines):
        if len(line) < 161:
            print(f"Fixing line {i+1} (length {len(line)}) by appending 'I's")
            line = line + "I" * (161 - len(line))
        fixed_lines.append(line)
        
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v3.txt", "w") as f:
        for line in fixed_lines:
            f.write(line + "\n")
            
    print("Wrote fixed stabilizers to stabilizers_161_v3.txt")

if __name__ == "__main__":
    fix_stabilizers()
