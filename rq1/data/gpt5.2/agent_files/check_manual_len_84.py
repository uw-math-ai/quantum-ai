import stim

def check_manual_len():
    s = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII"
    print(f"Length: {len(s)}")
    
    # Check if this matches the file content for the failed line
    with open("stabilizers_84_fixed.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    # The failed one is likely index 71 (from previous analysis).
    # Or let's find the one that matches ZZZZ at 72.
    
    found = False
    for i, line in enumerate(stabs):
        if line == s:
            print(f"Match found at index {i} with manual string (length {len(line)})")
            found = True
            
    if not found:
        print("No exact match found in file.")
        # Let's find similarly looking ones
        for i, line in enumerate(stabs):
            if "ZZZZIIIIIIII" in line:
                print(f"Potential match at {i}: {line} (len {len(line)})")

if __name__ == "__main__":
    check_manual_len()
