import stim

def verify_structure():
    with open("stabilizers_155.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Type 4: XXXXX
    type4_indices = []
    for i, line in enumerate(lines):
        s = line.lstrip('I')
        if s.startswith('XXXXX'):
            idx = line.find('XXXXX') // 5
            type4_indices.append(idx)
    
    print(f"Type 4 indices: {sorted(type4_indices)}")
    
    # Type 5: ZZZZZ
    type5_indices = []
    for i, line in enumerate(lines):
        s = line.lstrip('I')
        if s.startswith('ZZZZZ'):
            idx = line.find('ZZZZZ') // 5
            type5_indices.append(idx)
            
    print(f"Type 5 indices: {sorted(type5_indices)}")

if __name__ == "__main__":
    verify_structure()
