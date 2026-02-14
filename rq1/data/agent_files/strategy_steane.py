# Steane code generators check
# Row 1 (IIIXXXX): indices 3,4,5,6
# Row 2 (IXXIIXX): indices 1,2, 5,6
# Row 3 (XIXIXIX): indices 0,2, 4,6

# My extracted generators for block 0:
# 1. `XXIIXX...` (if padded to `XXIIXXI` or `XXIIXX`) -> Indices 0,1, 4,5
# 2. `XIXIXIX` -> Indices 0,2, 4,6
# 3. `IIIXXXX` -> Indices 3,4,5,6

# Let's compare.
# Standard:
# 1: 3,4,5,6 (Matches 3)
# 2: 1,2,5,6
# 3: 0,2,4,6 (Matches 2)

# My generator 1 is 0,1, 4,5.
# Standard generator 2 is 1,2, 5,6.
# They are different.
# Maybe a different permutation of Steane code?

# Also check Z generators.
# 13. `ZZIIZZ...` (Indices 0,1, 4,5?)
# 17. `ZIZIZIZ` (Indices 0,2, 4,6)
# 21. `IIIZZZZ` (Indices 3,4,5,6)

# So for each block of 7 qubits, we have 3 X and 3 Z generators.
# 4 blocks -> 4 * 3 = 12 X, 12 Z.
# Total 24 generators.
# Plus 2 global generators:
# 25. `XXXIIIIXXXIIIIXXXIIIIXXXIIII` (X on 0-2, 7-9, 14-16, 21-23?)
# 26. `ZZZIIIIZZZIIIIZZZIIIIZZZIIII` (Z on 0-2, 7-9, 14-16, 21-23?)

# Wait, let's look at 25 carefully.
# `XXXIIII` (7 chars) repeated 4 times?
# 28 chars.
# Indices 0,1,2 in each block are X.
# Indices 3,4,5,6 are I.

# So we have 4 independent blocks of 7 qubits.
# Each block has 6 stabilizers (3X, 3Z).
# This leaves 1 logical qubit per block.
# Total 4 logical qubits.
# The global generators (25, 26) act on these logical qubits?

# Let's see what logical operators correspond to.
# For Steane code, Logical X is XXXXXXX (all 7).
# Logical Z is ZZZZZZZ (all 7).
# Or maybe X on specific qubits.

# If we have 4 logical qubits, and we add 2 more stabilizers.
# We constrain 2 logical degrees of freedom.
# Remaining: 2 logical qubits encoded in 28 physical qubits.
# Total stabilizers = 24 + 2 = 26.
# 28 - 26 = 2. Consistent.

# My task is to prepare this state.
# Strategy:
# 1. Prepare 4 independent Steane code states (logical |0> or |+>?)
# 2. Then apply the global constraints.
# 3. Or just build the full tableau and Gaussian elimination.

# Given 28 qubits, Gaussian elimination might be slightly expensive for me to implement manually/debug, 
# but for the computer it is trivial. 
# However, `check_stabilizers_tool` only checks if I succeeded. It doesn't give me the state.

# I should use the Gaussian elimination approach to generate the circuit.
# I will write a script to do this.
# I need to be careful with the first stabilizer length.
# I'll pad it with II.
