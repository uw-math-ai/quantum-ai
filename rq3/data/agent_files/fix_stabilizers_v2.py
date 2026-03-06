def main():
    input_file = "data/stabilizers.txt"
    output_file = "data/stabilizers_fixed_v2.txt"
    
    with open(input_file, "r") as f:
        lines = [line.strip().replace(',', '') for line in f.readlines()]
    
    fixed_lines = []
    for i, line in enumerate(lines):
        if not line:
            continue
            
        # Specific fixes based on analysis
        if i == 58:
            # Shift left 2: Remove 2 from start, add 2 to end
            # But wait, removing 2 from start removes 'II' usually.
            # Check if start is 'II'.
            if line.startswith("II"):
                line = line[2:] + "II"
            else:
                print(f"Warning: Line 58 does not start with II. content: {line[:10]}")
                # If it doesn't start with II, maybe I shouldn't simply strip.
                # But analysis said start index is 152. So 0-151 are 'I'.
                # So safe to strip.
                line = line[2:] + "II"

        elif i == 59:
            # Length 182. Remove 2 from start.
            if len(line) == 182:
                line = line[2:]
            else:
                print(f"Warning: Line 59 length is {len(line)}")

        elif i in [48, 111, 136]:
            # Length 178. Pad end.
            if len(line) == 178:
                line = line + "II"
        
        # General check
        if len(line) != 180:
             print(f"Line {i} length {len(line)} still incorrect!")
        
        fixed_lines.append(line)
    
    with open(output_file, "w") as f:
        for line in fixed_lines:
            f.write(line + "\n")
            
    print(f"Saved {len(fixed_lines)} fixed stabilizers to {output_file}")

if __name__ == "__main__":
    main()
