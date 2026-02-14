import sys

def clean_and_analyze(filename):
    with open(filename, 'r') as f:
        # Read lines, strip whitespace, remove empty lines
        lines = [line.strip() for line in f if line.strip()]

    # Also remove any internal whitespace if present?
    # No, assuming they are contiguous strings.
    # But let's check.
    
    lengths = [len(l) for l in lines]
    if not lengths:
        print("No stabilizers found.")
        return

    majority_len = max(set(lengths), key=lengths.count)
    print(f"Majority length: {majority_len}")
    
    # Identify outliers
    outliers = [(i, l) for i, l in enumerate(lines) if len(l) != majority_len]
    if outliers:
        print(f"Found {len(outliers)} outliers.")
        for i, l in outliers:
            print(f"Line {i}: length {len(l)}: {l}")
    else:
        print("All lengths match.")

    # Write back clean
    with open(filename, 'w') as f:
        for l in lines:
            f.write(l + '\n')
            
    print(f"Number of stabilizers: {len(lines)}")

if __name__ == "__main__":
    clean_and_analyze('stabilizers_105.txt')
