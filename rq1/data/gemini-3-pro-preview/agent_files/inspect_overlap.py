stabs = []
with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]

def find_pattern(s):
    for i, c in enumerate(s):
        if c != 'I': return i
    return -1

s31 = stabs[31]
s140 = stabs[140]
print(f"S31 start: {find_pattern(s31)}")
print(f"S140 start: {find_pattern(s140)}")

# Check overlap
print(f"S31 at overlap: {s31[155:160]}")
print(f"S140 at overlap: {s140[155:160]}")

s32 = stabs[32]
s103 = stabs[103]
print(f"S32 start: {find_pattern(s32)}")
print(f"S103 start: {find_pattern(s103)}")

print(f"S32 at overlap: {s32[160:165]}")
print(f"S103 at overlap: {s103[160:165]}")

