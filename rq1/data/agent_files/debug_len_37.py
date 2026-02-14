def check_len():
    with open('target_stabilizers_60.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    l37 = lines[37]
    print(f"Line 37: '{l37}'")
    print(f"Length: {len(l37)}")
    
    # Check if prompt line 37 matches
    prompt_l37 = "IIIIIIIIIIIIIIIIIZIIZIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    print(f"Prompt len: {len(prompt_l37)}")
    
    if l37 == prompt_l37:
        print("Match!")
    else:
        print("Mismatch!")

if __name__ == "__main__":
    check_len()
