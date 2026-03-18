import stim

def check_consistency_prompt():
    with open("target_stabilizers_prompt.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
        
    print(f"Checking consistency of {len(lines)} stabilizers...")
    
    # Check pairwise commutation
    # This is O(N^2), might be slow for 119. 119^2 is small.
    
    # We need to convert to PauliStrings.
    # Note: they are length 119.
    paulis = [stim.PauliString(l) for l in lines]
    
    consistent = True
    for i in range(len(paulis)):
        for j in range(i+1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                print(f"Anticommutation between {i} and {j}")
                print(f"{i}: {lines[i]}")
                print(f"{j}: {lines[j]}")
                consistent = False
                break
        if not consistent:
            break
            
    if consistent:
        print("Stabilizers are consistent (all commute).")
    else:
        print("Stabilizers are inconsistent.")

if __name__ == "__main__":
    check_consistency_prompt()
