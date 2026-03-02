
def check_v3_line_28():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v3.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    print(f"v3 Line 28: {lines[28]}")
    
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v2.txt") as f:
        lines2 = [l.strip() for l in f if l.strip()]
    print(f"v2 Line 28: {lines2[28]}")

if __name__ == "__main__":
    check_v3_line_28()
