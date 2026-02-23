with open("data/gemini-3-pro-preview/agent_files/stabilizers_171.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

s = lines[18]
indices = [i for i, c in enumerate(s) if c == 'X']
print(f"Line 18 indices: {indices}")

s = lines[56]
indices = [i for i, c in enumerate(s) if c == 'Z']
print(f"Line 56 indices: {indices}")

s = lines[75]
indices = [i for i, c in enumerate(s) if c == 'Z' or c == 'I'] 
# identifying Z and I is not enough, need ZIZ pattern.
indices = [i for i, c in enumerate(s) if c != 'I']
print(f"Line 75 indices: {indices}")
print(f"Line 75 string at indices: {[s[i] for i in indices]}")
