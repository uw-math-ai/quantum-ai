with open('target_stabilizers_v2.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

print(f"Line 24: {lines[24]}")
print(f"Length 24: {len(lines[24])}")
print(f"Line 121: {lines[121]}")
print(f"Length 121: {len(lines[121])}")

# Fix line 24: Insert 'I' at index 4 to match pattern XXXXIII...
lines[24] = lines[24][:4] + 'I' + lines[24][4:]
print(f"Fixed 24: {lines[24]}")
print(f"Length 24: {len(lines[24])}")

# Check line 121 context
print(f"Line 120: {lines[120]}")
print(f"Line 122: {lines[122]}")

# Pattern for 121 seems to be XXIIIXXXIXIX...
# Let's compare lengths
print(f"Length 120: {len(lines[120])}")
print(f"Length 122: {len(lines[122])}")
