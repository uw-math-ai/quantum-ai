import stim

with open("data/gemini-3-pro-preview/agent_files/stabilizers_171.txt", "r") as f:
    stabilizers = [l.strip() for l in f if l.strip()]

target_indices = [18, 56, 75]

def commutes(s1, s2):
    # s1, s2 are strings
    cnt = 0
    for c1, c2 in zip(s1, s2):
        if c1 != 'I' and c2 != 'I' and c1 != c2:
            cnt += 1
    return cnt % 2 == 0

for i in target_indices:
    s1 = stabilizers[i]
    print(f"Checking stabilizer {i}...")
    for j, s2 in enumerate(stabilizers):
        if i == j: continue
        if not commutes(s1, s2):
            print(f"  Anticommutes with {j}")
            # print(f"  {s1}")
            # print(f"  {s2}")
