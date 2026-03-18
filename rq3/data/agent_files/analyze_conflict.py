def main():
    with open("data/stabilizers_fixed.txt", "r") as f:
        lines = [line.strip().replace(',', '') for line in f.readlines()]
    
    line = lines[22]
    non_i = [j for j, c in enumerate(line) if c != 'I']
    print(f"Line 22: Start {non_i[0]}, End {non_i[-1]}")
    print(f"Content: {line[non_i[0]:non_i[-1]+1]}")

    line58 = lines[58]
    non_i58 = [j for j, c in enumerate(line58) if c != 'I']
    print(f"Line 58: Start {non_i58[0]}, End {non_i58[-1]}")
    print(f"Content: {line58[non_i58[0]:non_i58[-1]+1]}")

if __name__ == "__main__":
    main()
