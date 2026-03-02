def find_pattern():
    with open("stabilizers_180_new.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    for i in range(70, 90):
        if i >= len(lines): break
        line = lines[i]
        idx = line.find("ZZIZZ")
        print(f"Line {i}: len={len(line)}, index of ZZIZZ={idx}")

if __name__ == "__main__":
    find_pattern()
