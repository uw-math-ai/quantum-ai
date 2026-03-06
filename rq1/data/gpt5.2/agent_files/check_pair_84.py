import stim

def deep_check():
    target_x_str = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIII"
    target_z_str = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII"
    
    s35 = stim.PauliString(target_x_str)
    s47_str = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZI"
    # Wait, line 47 in file is ZZZZ shifted.
    # Let's read from file to be sure.
    
    stabs = []
    with open("stabilizers_84_task.txt", "r") as f:
        stabs = [stim.PauliString(line.strip()) for line in f if line.strip()]
        
    s47 = stabs[47] # This is 48th stabilizer? Or 47th? 0-indexed.
    
    print(f"S35 (from str): {s35}")
    print(f"S47 (from file): {s47}")
    
    print(f"Commutes: {s35.commutes(s47)}")
    
    # Check overlap
    s35_s = str(s35)
    s47_s = str(s47)
    
    # First char is sign
    print("Indices where they differ and are not I:")
    cnt = 0
    for i in range(1, 85):
        c1 = s35_s[i]
        c2 = s47_s[i]
        if c1 != '_' and c2 != '_' and c1 != c2:
            print(f"Index {i-1}: {c1} vs {c2}")
            cnt += 1
            
    print(f"Anticommuting overlap count: {cnt}")

if __name__ == "__main__":
    deep_check()
