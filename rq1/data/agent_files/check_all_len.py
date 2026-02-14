def check_all_len():
    with open('target_stabilizers_60.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    for i, line in enumerate(lines):
        if len(line) != 60:
            print(f"Line {i}: Length {len(line)}")
            print(f"Content: {line}")

if __name__ == "__main__":
    check_all_len()
