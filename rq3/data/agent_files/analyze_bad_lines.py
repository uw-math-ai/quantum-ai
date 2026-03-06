def main():
    with open("data/stabilizers.txt", "r") as f:
        lines = [line.strip().replace(',', '') for line in f.readlines()]
    
    bad_indices = [48, 59, 111, 136]
    
    for i in bad_indices:
        line = lines[i]
        non_i = [(j, c) for j, c in enumerate(line) if c != 'I']
        print(f"Line {i} (len {len(line)}): {non_i}")

if __name__ == "__main__":
    main()
