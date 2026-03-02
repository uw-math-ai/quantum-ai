
def compare_lines():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v2.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Line 55 (index 55): {lines[55]}")
    print(f"Length: {len(lines[55])}")
    print(f"Line 63 (index 63): {lines[63]}")
    print(f"Length: {len(lines[63])}")

if __name__ == "__main__":
    compare_lines()
