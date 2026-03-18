def main():
    input_file = "data/stabilizers.txt"
    output_file = "data/stabilizers_fixed.txt"
    
    with open(input_file, "r") as f:
        lines = [line.strip().replace(',', '') for line in f.readlines()]
    
    fixed_lines = []
    for i, line in enumerate(lines):
        if not line:
            continue
            
        if len(line) > 180:
            print(f"Truncating line {i} from {len(line)} to 180")
            line = line[:180]
        elif len(line) < 180:
            print(f"Padding line {i} from {len(line)} to 180")
            line = line + "I" * (180 - len(line))
        
        fixed_lines.append(line)
    
    with open(output_file, "w") as f:
        for line in fixed_lines:
            f.write(line + "\n")
            
    print(f"Saved {len(fixed_lines)} fixed stabilizers to {output_file}")

if __name__ == "__main__":
    main()
