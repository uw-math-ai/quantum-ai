import stim

# The circuit for one block
block_circuit = stim.Circuit("""
H 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
CZ 11 17 11 13 11 12 10 18 10 17 10 12 7 17 7 15 7 14 7 12 6 17 6 16 6 15 6 14 6 12 6 9 6 8 5 18 5 17 5 13 5 9 4 18 4 17 4 16 4 13 3 18 3 16 3 13 3 12 3 9 3 8 2 18 2 17 2 13 2 8 1 16 1 15 1 9 1 8 0 16 0 14 0 9 0 8
H 18 17 16 15 14 13 12 9 8
""")

# We need 4 copies shifted by 19*k
full_circuit = stim.Circuit()

for k in range(4):
    offset = 19 * k
    # Shift targets
    shifted_block = stim.Circuit()
    for inst in block_circuit:
        targets = []
        for t in inst.targets_copy():
            if t.is_qubit_target:
                targets.append(t.value + offset)
            else:
                targets.append(t)
        shifted_block.append(inst.name, targets)
    full_circuit += shifted_block

# Now we have |+>_L on each block.
# This satisfies X_Bk = +1 for all k.
# Thus Global X = +1 is satisfied.
# But Global Z = Z_B0 Z_B1 Z_B2 Z_B3 is not satisfied (expectation 0).
# We need to project onto +1 eigenstate of Global Z.
# This is equivalent to preparing the GHZ state in the logical basis?
# |GHZ> = (|0000> + |1111>) / sqrt(2).
# Stabilizers: Z0Z1, Z1Z2, Z2Z3, X0X1X2X3.
# Our current state is |++++>. Stabilizers X0, X1, X2, X3.
# We want to change the logical state from |++++> to a state stabilized by X0X1X2X3 and Z0Z1Z2Z3?
# No, the Global Z is just ONE stabilizer Z0Z1Z2Z3.
# The Global X is X0X1X2X3.
# Are there other logical constraints?
# The problem gives 74 stabilizers for 76 qubits.
# 72 local (18 per block).
# 2 global.
# Total 74.
# So we have 2 logical qubits remaining encoded in the 76 physical qubits.
# The constraints are just:
# 1. Local stabs = +1.
# 2. X_B0 X_B1 X_B2 X_B3 = +1.
# 3. Z_B0 Z_B1 Z_B2 Z_B3 = +1.

# If we prepare |++++> (logical), we satisfy 1 and 2.
# But not 3.
# We need a logical state |L> such that X_all |L> = |L> and Z_all |L> = |L>.
# The state |++++> satisfies X_all.
# But Z_all |++++> = |- - - -> (product of minuses) = |++++>?
# No.
# |+> = (|0> + |1>).
# Z |+> = |- > = (|0> - |1>).
# Z_all |++++> = |----> = (|0>-|1>)(|0>-|1>)...
# This is NOT |++++>.
# However, if we take |L> = |0000> + |1111>?
# X_all (|0000> + |1111>) = |1111> + |0000> = |L>. (Satisfied).
# Z_all (|0000> + |1111>) = |0000> + (-1)^4 |1111> = |0000> + |1111> = |L>. (Satisfied).
# So the logical GHZ state (|0000> + |1111>) works!
# Actually, any state in the subspace stabilized by XXXX and ZZZZ works.
# GHZ state is one such state.
# Is it the only one?
# The stabilizers are Z1Z2, Z2Z3... for GHZ.
# Here we only have Z0Z1Z2Z3.
# So we have more freedom.
# But GHZ is a valid solution.

# So we need to prepare logical GHZ state.
# Logical CNOTs?
# We can do logical CNOTs if we have transversal CNOTs?
# The code on each block is likely a [19, 1, ?] code.
# Is it CSS?
# The stabilizers I analyzed earlier:
# XS: IIXIIXIIXX..., etc.
# ZS: IIZIIZIIZZ...
# It looks CSS-ish?
# Let's check if Xs and Zs are separate.
# In `analyze_76.py` output:
# Patterns like `IIXIIXIIXX...` (Pure X?)
# Patterns like `IIZIIZIIZZ...` (Pure Z?)
# Yes, they look separated in the list.
# 0-8 are X-only?
# 9-17 are Z-only?
# Let's check the list again.
# "IIXIIXIIXX..." (X)
# "IIZIIZIIZZ..." (Z)
# Yes, it looks like a CSS code.
# If it is CSS, then transversal CNOT is logical CNOT.
# So we can prepare GHZ state on 4 blocks by:
# 1. Prepare |+> on block 0.
# 2. Prepare |0> on blocks 1, 2, 3.
# 3. Apply CNOT(0, 1), CNOT(0, 2), CNOT(0, 3).
# Result: (|0000> + |1111>).

# But wait, my block circuit prepares |+>_L (stabilized by X_L).
# How to prepare |0>_L (stabilized by Z_L)?
# Just add Hadamard gates on the logical qubit?
# For CSS code, logical H might be transversal H?
# If the code is self-dual CSS?
# The X stabilizers look same as Z stabilizers but with X/Z swapped?
# Let's check.
# X0: IIXIIXIIXX...
# Z0: IIZIIZIIZZ...
# They are exactly the same pattern!
# So the code is self-dual CSS.
# So transversal Hadamard is logical Hadamard.
# So to prepare |0>_L, we just prepare |+>_L and apply transversal H (on all 19 qubits).
# Or simpler:
# The circuit for |+>_L is `block_circuit`.
# The circuit for |0>_L is `block_circuit` followed by H on all qubits.
# OR: Rotate the basis of the solver.
# Actually, just apply H on all qubits of the block after `block_circuit`.

# Strategy:
# 1. Block 0: Run `block_circuit`. (State |+>_L)
# 2. Block 1, 2, 3: Run `block_circuit` + H_all. (State |0>_L)
# 3. Apply logical CNOTs: CNOT_L(0, 1), CNOT_L(0, 2), CNOT_L(0, 3).
#    Logical CNOT is transversal CNOT (CNOT between q_i of block A and q_i of block B for all i).
#    Since it's CSS code with same X/Z stabilizers, CNOT is transversal.

# Result should be logical GHZ state.
# Let's try this.

full_circuit = stim.Circuit()

# Block 0: |+>
c0 = block_circuit.copy()
# Relabel targets to 0-18
# It is already 0-18.

# Block 1: |0>
c1 = block_circuit.copy()
# Shift to 19-37
for inst in c1:
    targets = []
    for t in inst.targets_copy():
        if t.is_qubit_target:
            targets.append(t.value + 19)
    inst.targets_copy() # Wait, modifying in place? No.
# I need to rebuild c1 properly.

def shift_circuit(circ, offset):
    new_c = stim.Circuit()
    for inst in circ:
        targets = []
        for t in inst.targets_copy():
            if t.is_qubit_target:
                targets.append(t.value + offset)
            else:
                targets.append(t)
        new_c.append(inst.name, targets)
    return new_c

c0 = shift_circuit(block_circuit, 0)
c1 = shift_circuit(block_circuit, 19)
c2 = shift_circuit(block_circuit, 38)
c3 = shift_circuit(block_circuit, 57)

# Add H to c1, c2, c3 to rotate |+> to |0>
# H on all qubits of the block
for k in range(1, 4):
    offset = 19 * k
    h_layer = stim.Circuit()
    h_layer.append("H", range(offset, offset + 19))
    if k == 1: c1 += h_layer
    if k == 2: c2 += h_layer
    if k == 3: c3 += h_layer

full_circuit += c0
full_circuit += c1
full_circuit += c2
full_circuit += c3

# Logical CNOTs
# CNOT(0, 1) -> transversal CX between 0..18 and 19..37
for i in range(19):
    full_circuit.append("CX", [i, i + 19])
    
# CNOT(0, 2)
for i in range(19):
    full_circuit.append("CX", [i, i + 38])
    
# CNOT(0, 3)
for i in range(19):
    full_circuit.append("CX", [i, i + 57])
    
# Verify with check_stabilizers_tool
print(full_circuit)
