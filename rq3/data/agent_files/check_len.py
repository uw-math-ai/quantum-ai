def check_len():
    max_len = 0
    with open("my_stabilizers_776.txt", "r") as f:
        for line in f:
            l = line.strip()
            if l:
                max_len = max(max_len, len(l))
    print(f"Max stabilizer length: {max_len}")

check_len()
