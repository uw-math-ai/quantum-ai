import stim

def analyze_comm():
    stabs = []
    with open("stabilizers_84_task.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabs.append(stim.PauliString(line))

    # Identify the failed ones
    # Based on the output, they are the ones with XXXX at 72 and ZZZZ at 72.
    # Let's find their indices in the list.
    
    failed_indices = []
    for i, s in enumerate(stabs):
        s_str = str(s)
        if "XXXXIIIIIIII" in s_str[-12:] or "ZZZZIIIIIIII" in s_str[-12:]:
            # Make sure it's the one at 72.
            # 84 - 12 = 72.
            # Check if index 72 is X or Z.
            if s_str[72] in "XZ":
                failed_indices.append(i)
                print(f"Candidate for failed: Index {i}, {s_str}")

    print("Failed indices:", failed_indices)
    
    # Check commutativity of failed ones with all others
    for f_idx in failed_indices:
        f_stab = stabs[f_idx]
        print(f"\nChecking commutativity for stabilizer {f_idx}: {f_stab}")
        for i, s in enumerate(stabs):
            if not f_stab.commutes(s):
                print(f"Anticommutes with stabilizer {i}: {s}")

if __name__ == "__main__":
    analyze_comm()
