
def check_line_77():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v3.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    idx = 77
    print(f"Line {idx} (index {idx}): {lines[idx]}")
    
    # Check neighbors
    print(f"Line {idx-1} (index {idx-1}): {lines[idx-1]}")
    print(f"Line {idx+1} (index {idx+1}): {lines[idx+1]}")

if __name__ == "__main__":
    check_line_77()
