import stim

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
    return stabs

stabs = load_stabilizers("data/gemini-3-pro-preview/agent_files/stabilizers_current.txt")

indices = [82, 83, 84]
for idx in indices:
    if 0 <= idx < len(stabs):
        print(f"Stabilizer {idx}:")
        s = stabs[idx]
        non_id = [i for i, c in enumerate(s) if c != 'I']
        print(f"  Non-identity at: {non_id}")
        print(f"  Operators: {[s[i] for i in non_id]}")
