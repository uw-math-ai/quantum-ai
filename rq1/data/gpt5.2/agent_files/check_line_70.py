def check_line_70_len():
    with open("stabilizers_84_fixed.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    line70 = lines[70]
    print(f"Line 70: {line70}")
    print(f"Length: {len(line70)}")

if __name__ == "__main__":
    check_line_70_len()
