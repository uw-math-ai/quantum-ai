import stim
import numpy as np

n = 175

# I'll reconstruct the stabilizers based on the clear pattern
# The problem has these classes of stabilizers:

# 1. XX...XX stabilizers - pattern XXIIIXX at positions (k, k+1, k+5, k+6) with various k
# 2. X...X stabilizers - pattern XIIIIX at positions (k, k+5) 
# 3. ZZ...ZZ stabilizers - pattern ZZIIIZZ at positions similar to XX
# 4. ZZ...Z stabilizers - similar to X pattern
# 5. Single Z stabilizers at specific positions
# 6. Large block stabilizers at the end

# Let me build stabilizers systematically:
stabilizers = []

# Group 1: XXIIIXX stabilizers
# 7 groups of 7 stabilizers each = 49 stabilizers
# Base offsets: 0, 2, 6, 8, 10, 12, 16
# Within each base, shift by 25 for 7 copies

xx_bases = [0, 2, 6, 8, 10, 12, 16]  # 7 different row patterns
for base in xx_bases:
    for block in range(7):  # 7 blocks of 25
        offset = base + block * 25
        if offset + 6 < n:
            s = ['I'] * n
            s[offset] = 'X'
            s[offset + 1] = 'X'
            s[offset + 5] = 'X'
            s[offset + 6] = 'X'
            stabilizers.append(''.join(s))

print(f"After XX group: {len(stabilizers)} stabilizers")

# Group 2: XIIIIX stabilizers (single X pairs)  
# 7 groups of 7 = 49 stabilizers
x_bases = [4, 5, 9, 10, 13, 14, 15]
for base in x_bases:
    for block in range(7):
        offset = base + block * 25
        if offset + 5 < n:
            s = ['I'] * n
            s[offset] = 'X'
            s[offset + 5] = 'X'
            stabilizers.append(''.join(s))

print(f"After X group: {len(stabilizers)} stabilizers")

# Group 3: ZZIIIZZ stabilizers
zz_bases = [5, 7, 10, 11, 12, 13, 17]
for base in zz_bases:
    for block in range(7):
        offset = base + block * 25
        if offset + 6 < n:
            s = ['I'] * n
            s[offset] = 'Z'
            s[offset + 1] = 'Z'
            s[offset + 5] = 'Z'
            s[offset + 6] = 'Z'
            stabilizers.append(''.join(s))

print(f"After ZZ group: {len(stabilizers)} stabilizers")

# Group 4: ZIIIIIZ stabilizers (single Z pairs)
z_bases = [1, 3, 8, 9, 14, 15, 18]
for base in z_bases:
    for block in range(7):
        offset = base + block * 25
        if offset + 5 < n:
            s = ['I'] * n
            s[offset] = 'Z'
            s[offset + 5] = 'Z'
            stabilizers.append(''.join(s))

print(f"After Z group: {len(stabilizers)} stabilizers")

# Group 5: Single Z at positions 0, 21, 23, etc.
single_z = [0, 21, 23, 46, 48, 69, 71, 92, 94, 113, 115, 136, 138, 161, 163, 173]
for pos in single_z:
    if pos < n:
        s = ['I'] * n
        s[pos] = 'Z'
        stabilizers.append(''.join(s))

# Group 6: IIZZ single positions
izz_positions = [2, 25, 27, 50, 52, 75, 77, 100, 102, 125, 127, 150, 152]
for pos in izz_positions:
    if pos < n:
        s = ['I'] * n
        s[pos] = 'Z'
        stabilizers.append(''.join(s))

print(f"After single Z groups: {len(stabilizers)} stabilizers")

# Now convert to PauliStrings and build circuit
print("\nBuilding circuit with Stim...")

try:
    pauli_strings = []
    for stab in stabilizers:
        pauli_strings.append(stim.PauliString(stab))
    
    # Use tableau method
    tableau = stim.Tableau.from_stabilizers(
        pauli_strings,
        allow_redundant=True,
        allow_underconstrained=True
    )
    
    circuit = tableau.to_circuit(method="elimination")
    print(f"Circuit has {len(circuit)} operations")
    print(circuit)
except Exception as e:
    print(f"Error: {e}")
