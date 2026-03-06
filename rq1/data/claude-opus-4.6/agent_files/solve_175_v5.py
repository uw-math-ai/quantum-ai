import stim

# All stabilizers for the 175 qubit task
stabs = []

# === Group 1: XXXX at positions 0,7,14,21,28,35,42,49,56,63,70,77,84,91,98,105,112,119,126,133,140,147,154,161,168 ===
for i in range(25):
    s = ['I'] * 175
    pos = i * 7
    for j in range(4):
        s[pos + j] = 'X'
    stabs.append(stim.PauliString(''.join(s)))

# === Group 2: XIXIXIX at positions 0,7,14,... (26 stabilizers) ===
for i in range(26):
    s = ['I'] * 175
    pos = i * 7
    if pos + 6 < 175:
        s[pos] = 'X'
        s[pos+2] = 'X'
        s[pos+4] = 'X'
        s[pos+6] = 'X'
        stabs.append(stim.PauliString(''.join(s)))

# === Group 3: XXXX at positions 2,9,16,23,... (25 stabilizers) ===
for i in range(25):
    s = ['I'] * 175
    pos = 2 + i * 7
    for j in range(4):
        s[pos + j] = 'X'
    stabs.append(stim.PauliString(''.join(s)))

# === Group 4: ZZZZ at positions 0,7,14,21,... (25 stabilizers) ===
for i in range(25):
    s = ['I'] * 175
    pos = i * 7
    for j in range(4):
        s[pos + j] = 'Z'
    stabs.append(stim.PauliString(''.join(s)))

# === Group 5: ZIZIZIZ at positions 0,7,14,... (26 stabilizers) ===
for i in range(26):
    s = ['I'] * 175
    pos = i * 7
    if pos + 6 < 175:
        s[pos] = 'Z'
        s[pos+2] = 'Z'
        s[pos+4] = 'Z'
        s[pos+6] = 'Z'
        stabs.append(stim.PauliString(''.join(s)))

# === Group 6: ZZZZ at positions 2,9,16,... (25 stabilizers) ===
for i in range(25):
    s = ['I'] * 175
    pos = 2 + i * 7
    for j in range(4):
        s[pos + j] = 'Z'
    stabs.append(stim.PauliString(''.join(s)))

# === Group 7: Complex X patterns ===
complex_x_patterns = [
    [1,2,4,6,8,9,11, 36,37,39,41,43,44,46],
    [69,70,72,74, 104,105,107,109,111,112,114],
    [43,44,46,48, 57,58,60,62,64,65,67],
    [113,114,116,118, 148,149,151,153,155,156,158],
    [15,16,18,20, 29,30,32,34,36,37,39],
    [71,72,74,76, 99,100,102,104,106,107,109],
    [50,51,53,55, 64,65,67,69,71,72,74],
    [120,121,123,125, 155,156,158,160,162,163,165],
]
for pattern in complex_x_patterns:
    s = ['I'] * 175
    for p in pattern:
        if p < 175:
            s[p] = 'X'
    stabs.append(stim.PauliString(''.join(s)))

# === Group 8: Simple X pairs ===
x_pairs = [
    [29,33,43,47],
    [36,40,50,54],
    [99,103,134,138],
    [106,110,141,145],
]
for pattern in x_pairs:
    s = ['I'] * 175
    for p in pattern:
        if p < 175:
            s[p] = 'X'
    stabs.append(stim.PauliString(''.join(s)))

# === Group 9: Complex Z patterns ===
complex_z_patterns = [
    [36,38,42,44, 71,73,77,79],
    [106,108,141,143,148,150],
    [8,10,14,16, 43,45,49,51],
    [71,73,113,115,120,122],
    [50,52,56,58, 85,87,91,93],
    [120,122,155,157,162,164],
    [22,24,28,30, 57,59,63,65],
    [85,87,127,129,134,136],
]
for pattern in complex_z_patterns:
    s = ['I'] * 175
    for p in pattern:
        if p < 175:
            s[p] = 'Z'
    stabs.append(stim.PauliString(''.join(s)))

# === Group 10: Simple Z pairs ===
z_pairs = [
    [1,3,7,9],
    [162,164,168,170],
    [15,17,21,23],
    [169,171,173],
]
for pattern in z_pairs:
    s = ['I'] * 175
    for p in pattern:
        if p < 175:
            s[p] = 'Z'
    stabs.append(stim.PauliString(''.join(s)))

print(f'Total stabilizers: {len(stabs)}')

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
