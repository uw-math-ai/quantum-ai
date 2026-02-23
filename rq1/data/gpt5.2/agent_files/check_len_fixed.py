def check_len_fixed():
    with open("stabilizers_84_fixed.txt", "r") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if len(line) != 84:
                print(f"Line {i} has length {len(line)}: {line}")
                
if __name__ == "__main__":
    check_len_fixed()
