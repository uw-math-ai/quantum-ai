import stim

def analyze_conflict():
    with open("stabilizers_180_new.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    s11 = lines[11]
    s83 = lines[83]
    
    print(f"S11 len: {len(s11)}")
    print(f"S83 len: {len(s83)}")

    p11 = stim.PauliString(s11)
    p83 = stim.PauliString(s83)
    
    print(f"S11: {s11}")
    print(f"S83: {s83}")
    
    if not p11.commutes(p83):
        print("They anticommute.")
        # Find overlap
        for i in range(len(s11)):
            c1 = s11[i]
            c2 = s83[i]
            if c1 != 'I' and c2 != 'I':
                print(f"Overlap at {i}: {c1} {c2}")
    else:
        print("They commute.")

if __name__ == "__main__":
    analyze_conflict()
