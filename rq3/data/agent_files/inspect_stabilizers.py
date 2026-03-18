def main():
    with open("data/stabilizers.txt", "r") as f:
        lines = f.readlines()
    
    print(f"Number of lines: {len(lines)}")
    lengths = [len(line.strip().replace(',', '')) for line in lines]
    print(f"Lengths: {lengths[:10]} ... {lengths[-10:]}")
    
    # Check if all lengths are equal
    unique_lengths = set(lengths)
    print(f"Unique lengths: {unique_lengths}")
    
    # Check total characters (ignoring whitespace)
    total_chars = sum(lengths)
    print(f"Total non-whitespace chars: {total_chars}")

if __name__ == "__main__":
    main()
