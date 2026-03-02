import sys
import numpy as np

def analyze_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    num_qubits = len(lines[0])
    num_stabilizers = len(lines)
    
    print(f"Number of stabilizers: {num_stabilizers}")
    print(f"Number of qubits: {num_qubits}")
    
    x_only = []
    z_only = []
    mixed = []
    
    for i, line in enumerate(lines):
        has_x = 'X' in line
        has_z = 'Z' in line
        if has_x and not has_z:
            x_only.append(i)
        elif has_z and not has_x:
            z_only.append(i)
        else:
            mixed.append(i)
            
    print(f"X-only stabilizers: {len(x_only)}")
    print(f"Z-only stabilizers: {len(z_only)}")
    print(f"Mixed stabilizers: {len(mixed)}")
    
    # Check for anticommutation
    anticommuting_pairs = []
    for i in range(num_stabilizers):
        for j in range(i + 1, num_stabilizers):
            s1 = lines[i]
            s2 = lines[j]
            anticommutes = False
            comm = 0
            for k in range(num_qubits):
                p1 = s1[k]
                p2 = s2[k]
                if p1 != 'I' and p2 != 'I' and p1 != p2:
                    comm += 1
            if comm % 2 == 1:
                anticommuting_pairs.append((i, j))
                
    print(f"Number of anticommuting pairs: {len(anticommuting_pairs)}")
    if anticommuting_pairs:
        print("First 10 pairs:", anticommuting_pairs[:10])

    # Check for shift structure
    # Many problems in this dataset have a shift structure.
    # Let's see if s[i+1] is a shift of s[i]
    
    shifts = []
    for i in range(num_stabilizers - 1):
        s1 = lines[i]
        s2 = lines[i+1]
        
        # Try to find shift amount
        # shift right by k
        best_k = 0
        
    # Just print the first few stabilizers to visually inspect
    print("\nFirst 5 stabilizers:")
    for i in range(5):
        print(lines[i])

if __name__ == "__main__":
    analyze_stabilizers(sys.argv[1])
