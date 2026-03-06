import stim
import sys
import os

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f.readlines() if line.strip()]
    return lines

def check_commutativity(stabilizers):
    # Create a tableau from the stabilizers (assuming they are Pauli strings)
    # We can check pairwise commutativity
    
    # Let's map I,X,Y,Z to 0,1,2,3 for internal representation or use stim
    # Actually Stim's Tableau.from_stabilizers will fail if they don't commute.
    try:
        t = stim.Tableau.from_stabilizers(stabilizers)
        print("Stabilizers commute and are independent.")
        return True, t
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return False, None

def analyze_structure(stabilizers):
    if not stabilizers:
        print("No stabilizers found.")
        return [], [], []
        
    n_qubits = len(stabilizers[0])
    n_stabs = len(stabilizers)
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {n_stabs}")
    
    # Identify X-only and Z-only stabilizers
    x_only = []
    z_only = []
    mixed = []
    for s in stabilizers:
        if all(c in 'IX' for c in s):
            x_only.append(s)
        elif all(c in 'IZ' for c in s):
            z_only.append(s)
        else:
            mixed.append(s)
            
    print(f"X-only stabilizers: {len(x_only)}")
    print(f"Z-only stabilizers: {len(z_only)}")
    print(f"Mixed stabilizers: {len(mixed)}")

    return x_only, z_only, mixed

if __name__ == "__main__":
    filename = "data/gemini-3-pro-preview/agent_files/stabilizers_171.txt"
    # Ensure absolute path
    abs_path = os.path.abspath(filename)
    print(f"Reading from {abs_path}")
    
    stabilizers = parse_stabilizers(filename)
    x_only, z_only, mixed = analyze_structure(stabilizers)
    commutes, tableau = check_commutativity(stabilizers)
    
    if not commutes:
        # Check pairwise
        print("Checking pairwise commutativity...")
        anticommutes_found = False
        count = 0
        for i in range(len(stabilizers)):
            for j in range(i + 1, len(stabilizers)):
                s1 = stabilizers[i]
                s2 = stabilizers[j]
                # Check commutativity
                cnt = 0
                for k in range(len(s1)):
                    p1 = s1[k]
                    p2 = s2[k]
                    if p1 != 'I' and p2 != 'I' and p1 != p2:
                        cnt += 1
                if cnt % 2 == 1:
                    print(f"Stabilizer {i} and {j} anticommute.")
                    # print(f"S{i}: {s1}")
                    # print(f"S{j}: {s2}")
                    count += 1
                    anticommutes_found = True
                    if count > 10: break
            if count > 10: break
