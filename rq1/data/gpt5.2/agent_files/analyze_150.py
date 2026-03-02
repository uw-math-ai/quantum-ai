import sys

def get_indices(s):
    indices = []
    for i, char in enumerate(s):
        if char != 'I':
            indices.append((i, char))
    return indices

def check_commutativity(s1, s2):
    anti_commute = 0
    for i in range(len(s1)):
        c1 = s1[i]
        c2 = s2[i]
        if c1 != 'I' and c2 != 'I' and c1 != c2:
            anti_commute += 1
    return anti_commute % 2 == 0

def solve():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_150.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    failed_strings = [
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIXXIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    ]
    
    failed_idxs = []
    for i, line in enumerate(lines):
        if line in failed_strings:
            failed_idxs.append(i)
            print(f"Stabilizer {i} failed.")
            # print(f"Indices: {get_indices(line)}")

    # Check commutativity of failed stabilizers with all others
    for idx in failed_idxs:
        s1 = lines[idx]
        found_anticommuting = False
        for i, s2 in enumerate(lines):
            if not check_commutativity(s1, s2):
                found_anticommuting = True
                print(f"Stabilizer {idx} anticommutes with {i}")
                # print(f"  {idx}: {s1}")
                # print(f"  {i}: {s2}")
                # print indices overlap
                # ind1 = get_indices(s1)
                # ind2 = get_indices(s2)
                # print(f"  Overlap: {[x for x in ind1 if x[0] in [y[0] for y in ind2]]}")
                # print(f"  Overlap: {[y for y in ind2 if y[0] in [x[0] for x in ind1]]}")
        if not found_anticommuting:
            print(f"Stabilizer {idx} commutes with everything.")

if __name__ == "__main__":
    solve()
