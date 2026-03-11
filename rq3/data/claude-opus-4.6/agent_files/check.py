import stim

# Build circuit that preserves the block structure
# Per block (7 qubits indexed 0-6):
#   XXIIXXI at 0,1,4,5 (corrected - no position 6!)
#   XIXIXIX at 0,2,4,6
#   IIIXXXX at 3,4,5,6
#   ZZIIZZI at 0,1,4,5 (corrected)
#   ZIZIZIZ at 0,2,4,6
#   IIIZZZZ at 3,4,5,6
# Plus global:
#   XXXIIII repeated (X on first 3 of each block)
#   ZZZIIII repeated (Z on first 3 of each block)

# Wait, let me recheck the stabilizers
stabs_str = """XXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXI"""

# First stabilizer: XXIIXX then rest I
# That's positions 0,1,4,5 (6 chars, not 7) then continuing...
s0 = stabs_str.strip().split('\n')[0]
print(f"Stab 0 length: {len(s0)}")
print(f"First 10 chars: {s0[:10]}")
for i, c in enumerate(s0):
    if c != 'I':
        print(f"  Position {i}: {c}")
