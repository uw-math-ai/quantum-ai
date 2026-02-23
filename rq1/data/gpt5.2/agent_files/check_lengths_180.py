def check_lengths():
    with open("stabilizers_180_new.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    for i, line in enumerate(lines):
        if len(line) != 180:
            print(f"Line {i} has length {len(line)}")

if __name__ == "__main__":
    check_lengths()
