def clean():
    with open('stabilizers_135.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    good = []
    for i, line in enumerate(lines):
        if len(line) == 135:
            good.append(line)
        else:
            print(f"Line {i}: len {len(line)}")
            # heuristic fix: if it's too long, maybe extra 'I' at end?
            # or maybe duplicate chars?
            # Let's just print it for now.
            print(line)

    if len(good) == len(lines):
        print("All good.")
    else:
        print(f"Found {len(lines) - len(good)} bad lines.")

if __name__ == "__main__":
    clean()
