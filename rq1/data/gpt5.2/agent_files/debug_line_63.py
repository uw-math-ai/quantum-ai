
def check_line_63():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v2.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Line 63 (index 63): {lines[63]}")
    print(f"Length: {len(lines[63])}")
    
    # Check surrounding lines too
    print(f"Line 62: {lines[62]}")
    print(f"Length: {len(lines[62])}")
    print(f"Line 64: {lines[64]}")
    print(f"Length: {len(lines[64])}")

if __name__ == "__main__":
    check_line_63()
