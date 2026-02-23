import stim

# All stabilizers for the 175 qubit task
# Reading from the original task specification carefully

# Build stabilizer list
stabs = []

# === Group 1: XXXX at positions 0,7,14,21,28,35,42,49,56,63,70,77,84,91,98,105,112,119,126,133,140,147,154,161,168 ===
# These are 25 stabilizers with XXXX shifted by 7 each time, starting at position 0
for i in range(25):
    s = ['I'] * 175
    pos = i * 7
    for j in range(4):
        s[pos + j] = 'X'
    stabs.append(''.join(s))

# === Group 2: XIXIXIX at positions 0,7,14,... (26 stabilizers) ===
# Pattern: X at pos, pos+2, pos+4, pos+6
for i in range(26):
    s = ['I'] * 175
    pos = i * 7
    if pos + 6 < 175:
        s[pos] = 'X'
        s[pos+2] = 'X'
        s[pos+4] = 'X'
        s[pos+6] = 'X'
        stabs.append(''.join(s))

# === Group 3: XXXX at positions 2,9,16,23,... (25 stabilizers) ===
# These are shifted versions starting at position 2
for i in range(25):
    s = ['I'] * 175
    pos = 2 + i * 7
    for j in range(4):
        s[pos + j] = 'X'
    stabs.append(''.join(s))

# === Group 4: ZZZZ at positions 0,7,14,21,... (25 stabilizers) ===
for i in range(25):
    s = ['I'] * 175
    pos = i * 7
    for j in range(4):
        s[pos + j] = 'Z'
    stabs.append(''.join(s))

# === Group 5: ZIZIZIZ at positions 0,7,14,... (26 stabilizers) ===
for i in range(26):
    s = ['I'] * 175
    pos = i * 7
    if pos + 6 < 175:
        s[pos] = 'Z'
        s[pos+2] = 'Z'
        s[pos+4] = 'Z'
        s[pos+6] = 'Z'
        stabs.append(''.join(s))

# === Group 6: ZZZZ at positions 2,9,16,... (25 stabilizers) ===
for i in range(25):
    s = ['I'] * 175
    pos = 2 + i * 7
    for j in range(4):
        s[pos + j] = 'Z'
    stabs.append(''.join(s))

# === Group 7: Complex X patterns (8 stabilizers) ===
# IXXIXIIIXXIX at positions with 35 offset
# Pattern 1: pos 1,2,4,6,8,9,11 and 36,37,39,41,43,44,46
complex_x_1 = ['I'] * 175
for p in [1,2,4,6,8,9,11, 36,37,39,41,43,44,46]:
    if p < 175:
        complex_x_1[p] = 'X'
stabs.append(''.join(complex_x_1))

# Pattern 2: pos 69,70,72,74, 104,105,107,109,111,112,114
complex_x_2 = ['I'] * 175
for p in [69,70,72,74, 104,105,107,109,111,112,114]:
    if p < 175:
        complex_x_2[p] = 'X'
stabs.append(''.join(complex_x_2))

# Pattern 3: 43,44,46,48, 57,58,60,62,64,65,67
complex_x_3 = ['I'] * 175
for p in [43,44,46,48, 57,58,60,62,64,65,67]:
    if p < 175:
        complex_x_3[p] = 'X'
stabs.append(''.join(complex_x_3))

# Pattern 4: 113,114,116,118, 148,149,151,153,155,156,158
complex_x_4 = ['I'] * 175
for p in [113,114,116,118, 148,149,151,153,155,156,158]:
    if p < 175:
        complex_x_4[p] = 'X'
stabs.append(''.join(complex_x_4))

# Pattern 5: 15,16,18,20, 29,30,32,34,36,37,39
complex_x_5 = ['I'] * 175
for p in [15,16,18,20, 29,30,32,34,36,37,39]:
    if p < 175:
        complex_x_5[p] = 'X'
stabs.append(''.join(complex_x_5))

# Pattern 6: 71,72,74,76, 99,100,102,104,106,107,109 (shifted)
complex_x_6 = ['I'] * 175
for p in [71,72,74,76, 99,100,102,104,106,107,109]:
    if p < 175:
        complex_x_6[p] = 'X'
stabs.append(''.join(complex_x_6))

# Pattern 7: 50,51,53,55, 64,65,67,69,71,72,74
complex_x_7 = ['I'] * 175
for p in [50,51,53,55, 64,65,67,69,71,72,74]:
    if p < 175:
        complex_x_7[p] = 'X'
stabs.append(''.join(complex_x_7))

# Pattern 8: 120,121,123,125, 155,156,158,160,162,163,165
complex_x_8 = ['I'] * 175
for p in [120,121,123,125, 155,156,158,160,162,163,165]:
    if p < 175:
        complex_x_8[p] = 'X'
stabs.append(''.join(complex_x_8))

# === Group 8: Simple X pairs (4 stabilizers) ===
# Pattern: XXIX at two positions separated by 14
x_pair_1 = ['I'] * 175
for p in [29,33,43,47]:
    if p < 175:
        x_pair_1[p] = 'X'
stabs.append(''.join(x_pair_1))

x_pair_2 = ['I'] * 175
for p in [36,40,50,54]:
    if p < 175:
        x_pair_2[p] = 'X'
stabs.append(''.join(x_pair_2))

x_pair_3 = ['I'] * 175
for p in [99,103,134,138]:
    if p < 175:
        x_pair_3[p] = 'X'
stabs.append(''.join(x_pair_3))

x_pair_4 = ['I'] * 175
for p in [106,110,141,145]:
    if p < 175:
        x_pair_4[p] = 'X'
stabs.append(''.join(x_pair_4))

# === Group 9: Complex Z patterns (8 stabilizers) ===
# IZZIZIIIZZIZ pairs
complex_z_1 = ['I'] * 175
for p in [36,38,42,44, 71,73,77,79]:
    if p < 175:
        complex_z_1[p] = 'Z'
stabs.append(''.join(complex_z_1))

complex_z_2 = ['I'] * 175
for p in [106,108,141,143,148,150]:
    if p < 175:
        complex_z_2[p] = 'Z'
stabs.append(''.join(complex_z_2))

complex_z_3 = ['I'] * 175
for p in [8,10,14,16, 43,45,49,51]:
    if p < 175:
        complex_z_3[p] = 'Z'
stabs.append(''.join(complex_z_3))

complex_z_4 = ['I'] * 175
for p in [71,73,113,115,120,122]:
    if p < 175:
        complex_z_4[p] = 'Z'
stabs.append(''.join(complex_z_4))

complex_z_5 = ['I'] * 175
for p in [50,52,56,58, 85,87,91,93]:
    if p < 175:
        complex_z_5[p] = 'Z'
stabs.append(''.join(complex_z_5))

complex_z_6 = ['I'] * 175
for p in [120,122,155,157,162,164]:
    if p < 175:
        complex_z_6[p] = 'Z'
stabs.append(''.join(complex_z_6))

complex_z_7 = ['I'] * 175
for p in [22,24,28,30, 57,59,63,65]:
    if p < 175:
        complex_z_7[p] = 'Z'
stabs.append(''.join(complex_z_7))

complex_z_8 = ['I'] * 175
for p in [85,87,127,129,134,136]:
    if p < 175:
        complex_z_8[p] = 'Z'
stabs.append(''.join(complex_z_8))

# === Group 10: Simple Z pairs (4 stabilizers) ===
z_pair_1 = ['I'] * 175
for p in [1,3,7,9]:
    if p < 175:
        z_pair_1[p] = 'Z'
stabs.append(''.join(z_pair_1))

z_pair_2 = ['I'] * 175
for p in [162,164,168,170]:
    if p < 175:
        z_pair_2[p] = 'Z'
stabs.append(''.join(z_pair_2))

z_pair_3 = ['I'] * 175
for p in [15,17,21,23]:
    if p < 175:
        z_pair_3[p] = 'Z'
stabs.append(''.join(z_pair_3))

z_pair_4 = ['I'] * 175
for p in [169,171,173]:
    if p < 175:
        z_pair_4[p] = 'Z'
stabs.append(''.join(z_pair_4))

print(f'Total stabilizers: {len(stabs)}')

# Verify all lengths are 175
for i, s in enumerate(stabs):
    if len(s) != 175:
        print(f'Error: stabilizer {i} has length {len(s)}')

# Generate circuit
try:
    tableau = stim.Tableau.from_stabilizers(stabs, allow_redundant=True, allow_underconstrained=True)
    circuit = tableau.to_circuit()
    print("Circuit generated successfully!")
    circuit_str = str(circuit)
    with open('circuit_175_gen.stim', 'w') as f:
        f.write(circuit_str)
    print(f"Circuit saved with {len(circuit_str.split(chr(10)))} lines")
    print(circuit_str[:1000])
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
