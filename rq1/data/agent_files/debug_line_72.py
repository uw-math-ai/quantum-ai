with open('stabilizers_105.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

line = lines[71] # index 71 is line 72
print(f"Length: {len(line)}")
print(line)

# Let's see if we can identify the extra characters.
# It should be 105 chars.
# Maybe extra 'I' somewhere?
