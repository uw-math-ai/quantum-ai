
def check_line_28():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v2.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Line 28 (index 28): {lines[28]}")
    print(f"Length: {len(lines[28])}")
    
    # Check surrounding lines too
    print(f"Line 27: {lines[27]}")
    print(f"Length: {len(lines[27])}")
    print(f"Line 29: {lines[29]}")
    print(f"Length: {len(lines[29])}")

if __name__ == "__main__":
    check_line_28()
