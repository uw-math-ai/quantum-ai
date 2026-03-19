import stim

# Original circuit string (cleaned up spaces)
original_circuit = """
CX 1 0 0 1 1 0
H 0
CX 0 2 0 3 0 8
H 1
CX 1 0 2 1 1 2 2 1 2 1 3 2 2 3 3 2 3 2 3 4 3 5 7 6 6 7 7 6 6 7 8 6 8 7
"""

# Define verification circuits
# Data qubits: 0-8
# Ancillas: 9-16 (8 ancillas for 8 stabilizers)
# Flags: 17, 18 (for the two X stabilizers)

# Map stabilizers to ancillas
# 0: XXXXXXIII (Ancilla 9, Flag 17)
# 1: XXXIIIXXX (Ancilla 10, Flag 18)
# 2: ZZIIIIIII (Ancilla 11)
# 3: ZIZIIIIII (Ancilla 12)
# 4: IIIZZIIII (Ancilla 13)
# 5: IIIZIZIII (Ancilla 14)
# 6: IIIIIIZZI (Ancilla 15)
# 7: IIIIIIZIZ (Ancilla 16)

verification_ops = []

# Initialization
verification_ops.append("R 9 10 11 12 13 14 15 16")

# --- X Stabilizers (Measure in X basis, use A as Control) ---
# Need to prepare A in |+> (H A)
verification_ops.append("H 9 10") 

# Stabilizer 0: X0 X1 X2 X3 X4 X5. Ancilla 9.
# Interleaved order: 0, 3, 1, 4, 2, 5 to catch partial errors via Z-stabilizers
verification_ops.append("CX 9 0 9 3 9 1 9 4 9 2 9 5")

# Stabilizer 1: X0 X1 X2 X6 X7 X8. Ancilla 10.
# Interleaved order: 0, 6, 1, 7, 2, 8
verification_ops.append("CX 10 0 10 6 10 1 10 7 10 2 10 8")

# Measure X-check ancillas in X basis -> H then M
verification_ops.append("H 9 10")

# --- Z Stabilizers (Measure in Z basis, use A as Target) ---
# Ancillas 11-16 in |0>
# ZZ checks: CX Data Ancilla

# Stabilizer 2: Z0 Z1. Ancilla 11.
verification_ops.append("CX 0 11 1 11")

# Stabilizer 3: Z0 Z2. Ancilla 12.
verification_ops.append("CX 0 12 2 12")

# Stabilizer 4: Z3 Z4. Ancilla 13.
verification_ops.append("CX 3 13 4 13")

# Stabilizer 5: Z3 Z5. Ancilla 14.
verification_ops.append("CX 3 14 5 14")

# Stabilizer 6: Z6 Z7. Ancilla 15.
verification_ops.append("CX 6 15 7 15")

# Stabilizer 7: Z6 Z8. Ancilla 16.
verification_ops.append("CX 6 16 8 16")

# Measurement
verification_ops.append("M 9 10 11 12 13 14 15 16")

# Combine
final_circuit_str = original_circuit.strip() + "\n" + "\n".join(verification_ops)

print(final_circuit_str)
