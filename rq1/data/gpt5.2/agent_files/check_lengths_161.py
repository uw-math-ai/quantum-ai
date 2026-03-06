
def check_all_lengths():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v2.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    for i, line in enumerate(lines):
        if len(line) != 161:
            print(f"Line {i+1} (index {i}) length: {len(line)}")
            # Suggest fix
            missing = 161 - len(line)
            if missing > 0:
                print(f"  Missing {missing} chars. Suggest appending 'I's.")
            else:
                print(f"  Extra {-missing} chars.")

if __name__ == "__main__":
    check_all_lengths()
