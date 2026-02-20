stabs = []
with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]

def check_comm(i, j):
    import stim
    s1 = stim.PauliString(stabs[i])
    s2 = stim.PauliString(stabs[j])
    comm = s1.commutes(s2)
    print(f"{i} vs {j}: commutes={comm}")
    print(f"  {i}: {stabs[i]}")
    print(f"  {j}: {stabs[j]}")

pairs = [(31, 140), (32, 103), (32, 144), (32, 145), (32, 154), (32, 155)]
for i, j in pairs:
    check_comm(i, j)
