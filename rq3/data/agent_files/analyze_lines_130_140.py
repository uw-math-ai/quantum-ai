def main():
    with open("data/stabilizers.txt", "r") as f:
        lines = [line.strip().replace(',', '') for line in f.readlines()]
    
    for i in range(130, 141):
        line = lines[i]
        non_i = [j for j, c in enumerate(line) if c != 'I']
        if non_i:
            print(f"Line {i} (len {len(line)}): Start {non_i[0]}, End {non_i[-1]}")

if __name__ == "__main__":
    main()
