import stim

def check_overlap_final():
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed_final.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    s34 = lines[34]
    s79 = lines[79]
    
    print(f"Line 34: {s34}")
    print(f"Line 79: {s79}")
    
    ps34 = stim.PauliString(s34)
    ps79 = stim.PauliString(s79)
    
    print(f"Commutes: {ps34.commutes(ps79)}")
    
    xs34 = [k for k, c in enumerate(s34) if c == 'X']
    zs79 = [k for k, c in enumerate(s79) if c == 'Z']
    
    print(f"Xs 34: {xs34}")
    print(f"Zs 79: {zs79}")
    
    overlap = set(xs34).intersection(set(zs79))
    print(f"Overlap: {overlap}")

if __name__ == "__main__":
    check_overlap_final()
