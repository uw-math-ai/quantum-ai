filename = "data/gemini-3-pro-preview/agent_files/stabilizers_90.txt"
with open(filename, "r") as f:
    lines = [line.strip().replace(',', '') for line in f if line.strip()]

line36 = lines[35]
line37 = lines[36]
line38 = lines[37]

print(f"Line 36 len: {len(line36)}")
print(f"Line 37 len: {len(line37)}")
print(f"Line 38 len: {len(line38)}")

def count_leading_Is(s):
    count = 0
    for c in s:
        if c == 'I':
            count += 1
        else:
            break
    return count

print(f"Line 36 leading Is: {count_leading_Is(line36)}")
print(f"Line 37 leading Is: {count_leading_Is(line37)}")
print(f"Line 38 leading Is: {count_leading_Is(line38)}")
