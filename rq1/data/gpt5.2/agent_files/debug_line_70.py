
def check_line_70():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v2.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    if len(lines) > 70:
        print(f"Line 70 (index 70): {lines[70]}")
        print(f"Length: {len(lines[70])}")
    else:
        print("Not enough lines")

if __name__ == "__main__":
    check_line_70()
