def main():
    with open("data/stabilizers.txt", "r") as f:
        lines = [line.strip().replace(',', '') for line in f.readlines()]
    
    for i, line in enumerate(lines):
        if len(line) != 180:
            print(f"Line {i}: Length {len(line)}")
            print(f"Content: {line[:20]}...")

if __name__ == "__main__":
    main()
