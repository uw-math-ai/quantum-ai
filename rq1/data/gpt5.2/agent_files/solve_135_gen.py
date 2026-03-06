import stim

# Generate stabilizers based on patterns
stabilizers = []

# Block 0: XXXXXX (shift 9)
# 15 items. Indices 0-14.
for i in range(15):
    s = ['I'] * 135
    start = i * 9
    for j in range(6):
        if start + j < 135:
            s[start + j] = 'X'
    stabilizers.append("".join(s))

# Block 1: XXXIIIXXX (shift 9)
# 15 items. Indices 15-29.
for i in range(15):
    s = ['I'] * 135
    start = i * 9
    # XXX at start
    for j in range(3):
        if start + j < 135:
            s[start + j] = 'X'
    # XXX at start + 6
    for j in range(3):
        if start + 6 + j < 135:
            s[start + 6 + j] = 'X'
    stabilizers.append("".join(s))

# Block 2: ZZ (shift 9)
# 15 items. Indices 30-44.
for i in range(15):
    s = ['I'] * 135
    start = i * 9
    # ZZ at start
    for j in range(2):
        if start + j < 135:
            s[start + j] = 'Z'
    stabilizers.append("".join(s))

# Block 3: IZZIZZ (shift 9)
# 15 items. Indices 45-59.
# The prompt started with IZZIZZ (index 45).
# IZZIZZ is I, Z, Z, I, Z, Z.
# Indices 1, 2, 4, 5 are Z.
for i in range(15):
    s = ['I'] * 135
    start = i * 9
    # IZZIZZ pattern relative to start
    # Z at 1, 2
    for j in [1, 2]:
        if start + j < 135:
            s[start + j] = 'Z'
    # Z at 4, 5
    for j in [4, 5]:
        if start + j < 135:
            s[start + j] = 'Z'
    stabilizers.append("".join(s))

# Block 4: IIIZZ (shift 9) - Wait, prompt had IIIZZII...
# 15 items. Indices 60-74.
for i in range(15):
    s = ['I'] * 135
    start = i * 9
    # IIIZZ relative to start -> Z at 3, 4
    for j in [3, 4]:
        if start + j < 135:
            s[start + j] = 'Z'
    stabilizers.append("".join(s))

# Block 5: IIIZIZ (shift 9)
# 15 items. Indices 75-89.
# Prompt had IIIZIZ...
# Z at 3, 5
for i in range(15):
    s = ['I'] * 135
    start = i * 9
    for j in [3, 5]:
        if start + j < 135:
            s[start + j] = 'Z'
    stabilizers.append("".join(s))

# Block 6: IIIIIIZZ (shift 9)
# 15 items. Indices 90-104.
# Z at 6, 7
for i in range(15):
    s = ['I'] * 135
    start = i * 9
    for j in [6, 7]:
        if start + j < 135:
            s[start + j] = 'Z'
    stabilizers.append("".join(s))

# Block 7: IIIIIIZIZ (shift 9)
# 15 items. Indices 105-119.
# Z at 6, 8
for i in range(15):
    s = ['I'] * 135
    start = i * 9
    for j in [6, 8]:
        if start + j < 135:
            s[start + j] = 'Z'
    stabilizers.append("".join(s))

# Block 8: XXXIIIIIIXXX (shift 9)
# 15 items. Indices 120-134.
# X at 0,1,2 and 9,10,11
for i in range(15):
    s = ['I'] * 135
    start = i * 9
    # XXX at start
    for j in range(3):
        if start + j < 135:
            s[start + j] = 'X'
    # XXX at start + 9? No, prompt had XXX...XXX
    # Wait, line 130 in solve_135.py was XXX...XXX.
    # It was XXXIIIIIIXXX. 6 Is in middle.
    # So X at 0,1,2 and 9,10,11.
    for j in range(3):
        if start + 9 + j < 135:
            s[start + 9 + j] = 'X'
    stabilizers.append("".join(s))

# Last block (ZIIZIIZ...)
# Wait, I listed 9 blocks of 15. That is 135 items.
# But solve_135_new.py had a block of `ZIIZIIZ` at the end (lines 131-138).
# This means there are MORE than 135 stabilizers or my block sizes are wrong?
# The prompt showed `ZIIZIIZ` lines at the end.
# This might be Block 8? Or Block 9?
# If there are 135 qubits, maybe 135 stabilizers?
# But if I have 9 blocks of 15, that's 135.
# Let's check the prompt for Block 8 again.
# Prompt last lines:
# ZIIZIIZIIZ...
# IIIIIIIIIZIIZIIZ...
# ...
# This looks like `ZIIZIIZ` (Z at 0, 3, 6).
# Shift 9.
# Is this Block 8?
# My Block 8 above was `XXXIIIIIIXXX`.
# I saw `XXX` lines near end of `solve_135_new.py`.
# Let's check `solve_135_new.py` again.
# Line 124 (index 121) `XXX...`
# Line 131 (index 128) `ZIIZ...`
# So maybe Block 8 is `ZIIZIIZ`?
# And Block 7 is `XXXIIIIIIXXX`?
# Or maybe there are 10 blocks?

# Let's assume the prompt is correct and reconstruct based on patterns I see.
# I will use the generated stabilizers to attempt a solution.
# But I need to be sure about the blocks.
# If I use `solve_135_try_3.py` which was copy-pasted (mostly), it failed.
# It failed because of anticommutation.
# This implies my patterns are consistent with the prompt but the prompt has anticommutation?
# NO, `S0` and `S54` anticommuted in `try_3`.
# `S54` was `IIZZIZZ` (index 9 in block 3).
# If block 3 (IZZIZZ) shift is 9.
# Index 54 should be [81-86].
# `S0` is [0-5].
# They don't overlap.
# So `S54` in `try_3` was WRONG (it was `IIZZIZZ` at start).
# This means `try_3` had WRONG stabilizers.
# So I should use the generated stabilizers script which enforces the correct shift!

print(f"Generated {len(stabilizers)} stabilizers.")

try:
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
    circuit = tableau.to_circuit("elimination")
    
    with open("circuit_135.stim", "w") as f:
        f.write(str(circuit))
    print("Circuit generated successfully.")
except Exception as e:
    print(f"Error: {e}")
