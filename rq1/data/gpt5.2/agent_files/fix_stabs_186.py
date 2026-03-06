import stim

def reparse_stabilizers():
    # We will read the raw prompt text which I will paste here.
    # To be safe, I'll put the raw string into a variable.
    # Wait, the prompt is huge. I should just copy the logic to read the existing file 
    # and assume it contains one stabilizer per line OR comma separated.
    
    # Let's inspect the file content first to see if it's correct.
    with open("stabilizers_186.txt", "r") as f:
        content = f.read()
    
    # If the file contains commas, we should split by commas.
    if ',' in content:
        parts = content.replace('\n', '').split(',')
        stabilizers = [p.strip() for p in parts if p.strip()]
    else:
        # One per line
        stabilizers = [line.strip() for line in content.split('\n') if line.strip()]

    # Now verify commutativity again with the cleaned list
    stabs = [stim.PauliString(s) for s in stabilizers]
    
    bad_pairs = []
    for i in range(len(stabs)):
        for j in range(i+1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                bad_pairs.append((i, j))
    
    print(f"Found {len(stabs)} stabilizers.")
    print(f"Anticommutes: {len(bad_pairs)}")
    if bad_pairs:
        print(f"First bad pair: {bad_pairs[0]}")
        i, j = bad_pairs[0]
        print(f"S[{i}]: {stabs[i]}")
        print(f"S[{j}]: {stabs[j]}")
    
    # Print indices
    def print_indices(s, idx):
        print(f"Stabilizer {idx} support:")
        for k in range(len(s)):
            if s[k] != 0: # 0 is I, 1 is X, 2 is Y, 3 is Z
                print(f"  {k}: {stim.PauliString('I'*k + 'X' + 'I'*(len(s)-k-1))[k] if s[k]==1 else ('Y' if s[k]==2 else 'Z')}")
    
    if bad_pairs:
        i, j = bad_pairs[0]
        print_indices(stabs[i], i)
        print_indices(stabs[j], j)

    # Save the cleaned list to a new file
    with open("stabilizers_186_clean.txt", "w") as f:
        for s in stabilizers:
            f.write(s + "\n")

if __name__ == "__main__":
    reparse_stabilizers()
