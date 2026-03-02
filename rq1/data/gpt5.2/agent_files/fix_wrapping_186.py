import stim

def fix_wrapping():
    with open("stabilizers_186.txt", "r") as f:
        content = f.read()
    
    # Remove all newlines and spaces and commas
    clean_content = content.replace('\n', '').replace(' ', '').replace(',', '').strip()
    
    # Split into chunks of 186
    n = 186
    stabilizers = []
    for i in range(0, len(clean_content), n):
        chunk = clean_content[i:i+n]
        if len(chunk) == n:
            stabilizers.append(chunk)
        else:
            print(f"Warning: Last chunk length is {len(chunk)}, expected {n}")

    # If index 105 is short, pad it?
    # Or analyze why it is short.
    if len(stabilizers) > 105:
        s105 = stabilizers[105]
        print(f"S105 len: {len(s105)}")
        # Check against pattern. It looks like it should match others.
        # Maybe missing 'II' at the end?
        # Or maybe missing 'II' in the middle?
        # Let's pad with 'I' to 186 and see if it commutes!
        if len(s105) < 186:
            diff = 186 - len(s105)
            # Try adding diff I's at end
            candidate = s105 + 'I' * diff
            stabilizers[105] = candidate
            print(f"Padded S105 with {diff} I's at end. New len: {len(candidate)}")
    
    # Verify commutativity again
    stabs = [stim.PauliString(s) for s in stabilizers]
    bad_pairs = []
    for i in range(len(stabs)):
        for j in range(i+1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                bad_pairs.append((i, j))

    print(f"Anticommutes: {len(bad_pairs)}")
    
    if len(bad_pairs) == 0:
        with open("stabilizers_186_fixed.txt", "w") as f:
            for s in stabilizers:
                f.write(s + "\n")
        print("Written to stabilizers_186_fixed.txt")
        
        # Also create a solve script using the fixed file
        solve_script = """import stim

def solve():
    with open("stabilizers_186_fixed.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    
    # Use elimination to find a state
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    circuit = tableau.to_circuit(method="elimination")
    print(circuit)

if __name__ == "__main__":
    solve()
"""
        with open("solve_186_fixed.py", "w") as f:
            f.write(solve_script)
            
if __name__ == "__main__":
    fix_wrapping()
