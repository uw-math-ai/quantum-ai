import stim

# All 174 stabilizers for 175 qubits
# First group: XXXX at positions 0,7,14,21,28,35,42,49,56,63,70,77,84,91,98,105,112,119,126,133,140,147,154,161,168
stabs = []

# Group 1: XXXX blocks (25 stabilizers) - shifted by 7
for i in range(25):
    s = ['I'] * 175
    pos = i * 7
    for j in range(4):
        s[pos + j] = 'X'
    stabs.append(''.join(s))

# Group 2: XIXIXIX blocks (26 stabilizers) - shifted by 7
for i in range(26):
    s = ['I'] * 175
    pos = i * 7
    s[pos] = 'X'
    s[pos+2] = 'X'
    s[pos+4] = 'X'
    s[pos+6] = 'X'
    stabs.append(''.join(s))

# Group 3: XXXX at positions 2,9,16,... (25 stabilizers) - shifted by 7, starting at 2
for i in range(25):
    s = ['I'] * 175
    pos = 2 + i * 7
    for j in range(4):
        s[pos + j] = 'X'
    stabs.append(''.join(s))

# Group 4: ZZZZ blocks (25 stabilizers) - shifted by 7
for i in range(25):
    s = ['I'] * 175
    pos = i * 7
    for j in range(4):
        s[pos + j] = 'Z'
    stabs.append(''.join(s))

# Group 5: ZIZIZIZ blocks (26 stabilizers) - shifted by 7
for i in range(26):
    s = ['I'] * 175
    pos = i * 7
    s[pos] = 'Z'
    s[pos+2] = 'Z'
    s[pos+4] = 'Z'
    s[pos+6] = 'Z'
    stabs.append(''.join(s))

# Group 6: ZZZZ at positions 2,9,16,... (25 stabilizers) - shifted by 7, starting at 2
for i in range(25):
    s = ['I'] * 175
    pos = 2 + i * 7
    for j in range(4):
        s[pos + j] = 'Z'
    stabs.append(''.join(s))

# Group 7: Complex X patterns - IXXIXIIIXXIX pairs
# Pattern: IXXIXIIIXXIX at pos, repeated at pos+35
complex_x_patterns = [
    (1, 4, 6, 8, 11, 36, 39, 41, 43, 46),  # stab 152
    (69, 72, 74, 104, 107, 109, 111, 114),  # stab 153
    (43, 46, 48, 57, 60, 62, 64, 67),  # stab 154
    (113, 116, 118, 148, 151, 153, 155, 158),  # stab 155
    (15, 18, 20, 29, 32, 34, 36, 39),  # stab 156
    (78, 81, 83, 92, 95, 97, 99, 102),  # stab 157
    (50, 53, 55, 64, 67, 69, 71, 74),  # stab 158
    (120, 123, 125, 155, 158, 160, 162, 165),  # stab 159
    (29, 33, 43, 47),  # stab 160
    (36, 40, 50, 54),  # stab 161
    (99, 103, 134, 138),  # stab 162
    (106, 110, 141, 145),  # stab 163
]

# Group 8: Complex Z patterns - IZZIZIIIZZIZ pairs
complex_z_patterns = [
    (36, 38, 42, 44, 71, 73, 77, 79),  # stab 164
    (106, 108, 141, 143, 148, 150),  # stab 165
    (8, 10, 14, 16, 43, 45, 49, 51),  # stab 166
    (78, 80, 113, 115, 120, 122),  # stab 167
    (50, 52, 56, 58, 85, 87, 91, 93),  # stab 168
    (120, 122, 155, 157, 162, 164),  # stab 169
    (22, 24, 28, 30, 57, 59, 63, 65),  # stab 170
    (92, 94, 127, 129, 134, 136),  # stab 171
    (1, 3, 7, 9),  # stab 172
    (162, 164, 168, 170),  # stab 173
    (15, 17, 21, 23),  # stab 174
    (169, 171),  # stab 175
]

print(f"Built {len(stabs)} stabilizers")

# Verify lengths
for i, s in enumerate(stabs):
    if len(s) != 175:
        print(f"Stabilizer {i} has wrong length: {len(s)}")

# Use stim.Tableau.from_stabilizers
try:
    tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=True, allow_underconstrained=True)
    circuit = tableau.to_circuit()
    print("Circuit generated successfully!")
    with open('circuit_175_gen.stim', 'w') as f:
        f.write(str(circuit))
    print(f"Circuit saved with {len(str(circuit).split(chr(10)))} lines")
except Exception as e:
    print(f"Error: {e}")
