import stim

with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]

# Indices 34 and 54 failed.
# Let's check if they are consistent with the other kept ones.
removed = [32, 33, 66, 104, 140]
kept_indices = [i for i in range(len(stabs)) if i not in removed]

# Pad
for i in range(len(stabs)):
    if len(stabs[i]) < 180:
        stabs[i] = stabs[i] + 'I' * (180 - len(stabs[i]))

kept_paulis = [stim.PauliString(stabs[i]) for i in kept_indices]

# Check consistency
try:
    tableau = stim.Tableau.from_stabilizers(kept_paulis, allow_underconstrained=True, allow_redundant=False)
    print("All kept stabilizers are independent and consistent.")
except Exception as e:
    print(f"Consistency check failed: {e}")
    # If redundant but inconsistent, maybe we can identify which ones.
    
    # Try adding them one by one
    good_indices = []
    good_paulis = []
    for idx in kept_indices:
        p = stim.PauliString(stabs[idx])
        try:
            # check if p is consistent with current tableau
            # This is hard without full tableau tracking.
            # But let's build incrementally.
            # actually stim.Tableau.from_stabilizers is fast.
            test_paulis = good_paulis + [p]
            stim.Tableau.from_stabilizers(test_paulis, allow_underconstrained=True, allow_redundant=True)
            good_indices.append(idx)
            good_paulis.append(p)
        except Exception as e:
            print(f"Stabilizer {idx} is inconsistent with previous ones: {e}")
