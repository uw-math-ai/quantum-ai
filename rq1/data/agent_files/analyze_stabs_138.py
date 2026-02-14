import sys

def analyze():
    # Load stabilizers
    with open("target_stabilizers_138.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("No stabilizers found")
        return

    n = len(lines[0])
    print(f"Number of qubits: {n}")
    print(f"Number of stabilizers: {len(lines)}")

    # Check if 138
    if n != 138:
        print(f"WARNING: Expected 138 qubits, found {n}")
    
    # Try to find block structure
    # 138 is 6 * 23.
    # Let's see if the stabilizers are shifts of each other.
    
    # Let's print the first few stabilizers to see the pattern
    for i, s in enumerate(lines):
        # find the support
        support = [j for j, c in enumerate(s) if c != 'I']
        if not support:
            print(f"Stab {i}: Identity")
            continue
        min_idx = min(support)
        max_idx = max(support)
        print(f"Stab {i}: support range [{min_idx}, {max_idx}], len {max_idx - min_idx + 1}, type {s[min_idx:max_idx+1]}")

if __name__ == "__main__":
    analyze()
