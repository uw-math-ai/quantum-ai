import stim
import numpy as np

# All original stabilizers
stabilizers_raw = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXI",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXX",
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZI",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZ",
    "XXXIIIIXXXIIIIIIIIIIIIIIIIXXXIIIIXXXIIIIIIIIIIIII",
    "XXXIIIIIIIIIIIXXXIIIIIIIIIXXXIIIIIIIIIIIXXXIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXIIIIXXXIIIIXXXIIIIXXXIIII",
    "ZZZIIIIZZZIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIIIIIIII",
    "ZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIZZZIIIIZZZIIII",
]

stabilizers = stabilizers_raw

# Group stabilizers by type
X_stabs = [s for s in stabilizers if 'X' in s and 'Z' not in s]
Z_stabs = [s for s in stabilizers if 'Z' in s and 'X' not in s]

print(f"X-type stabilizers: {len(X_stabs)}")
print(f"Z-type stabilizers: {len(Z_stabs)}")

# The stabilizers have anti-commutation between X and Z types when they overlap
# This suggests a CSS code structure where we need to prepare carefully

# Let me analyze: each block of 7 qubits has 6 local stabilizers (3X + 3Z)
# Plus 6 cross-block stabilizers (3X + 3Z) connecting the blocks

# For a CSS code |0_L>, we need to prepare:
# 1. A superposition over codewords (X stabilizers define code space)
# 2. That satisfies Z stabilizers (eigenvalue +1)

# Approach: Build GHZ-like states within blocks, then connect blocks

def build_css_circuit():
    circuit = stim.Circuit()
    n_qubits = 49
    
    # The code structure is 7 blocks of 7 qubits
    # Within each block: prepare entangled state
    
    # Step 1: For each block, prepare superposition
    # Based on X stabilizers, we need specific H patterns
    
    # For 7 qubits, the X stabilizers define:
    # XXIIXX_ (0,1,4,5)
    # XIXIXI_ (0,2,4,6)  
    # IIIXXXX (3,4,5,6)
    # => X on qubit 4 is common to all
    
    # Prepare each block with H on anchor qubit, then CNOT to spread
    for b in range(7):
        base = b * 7
        # Put all qubits in |+> initially for X stabilizers
        for i in range(7):
            circuit.append("H", [base + i])
    
    # Now create Z stabilizers via CZ
    # Z stabilizers within block:
    # ZZIIZZ_ (0,1,4,5)
    # ZIZIZIZ (0,2,4,6)
    # IIIZZZZ (3,4,5,6)
    
    # The Z stabilizers create correlation in the Z basis
    # CZ between (i,j) means Z_i Z_j is +1 for the state |++...+>
    
    for b in range(7):
        base = b * 7
        # For ZZIIZZ: need Z0Z1, Z4Z5 correlations and Z0Z4, Z1Z5
        circuit.append("CZ", [base+0, base+1])
        circuit.append("CZ", [base+4, base+5])
        circuit.append("CZ", [base+0, base+4])
        circuit.append("CZ", [base+1, base+5])
        
        # For ZIZIZIZ: need Z0Z2, Z2Z4, Z4Z6
        circuit.append("CZ", [base+0, base+2])
        circuit.append("CZ", [base+2, base+4])
        circuit.append("CZ", [base+4, base+6])
        
        # For IIIZZZZ: need Z3Z4, Z4Z5, Z5Z6 (some already done)
        circuit.append("CZ", [base+3, base+4])
        circuit.append("CZ", [base+3, base+5])
        circuit.append("CZ", [base+3, base+6])
    
    # Cross-block Z stabilizers
    # ZZZIIIIZZZIIIIIIIIIIIIIIIIIZZZIIIIIZZZIIIIIIIIIII
    # Blocks 0,1,3,4 with qubits 0,1,2 in each
    for i in range(3):
        circuit.append("CZ", [0+i, 7+i])   # block 0 to block 1
        circuit.append("CZ", [0+i, 21+i])  # block 0 to block 3  
        circuit.append("CZ", [7+i, 28+i])  # block 1 to block 4
        circuit.append("CZ", [21+i, 28+i]) # block 3 to block 4
    
    # ZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIII
    # Blocks 0,2,3,5 with qubits 0,1,2 in each
    for i in range(3):
        circuit.append("CZ", [0+i, 14+i])  # block 0 to block 2
        circuit.append("CZ", [14+i, 21+i]) # block 2 to block 3
        circuit.append("CZ", [21+i, 35+i]) # block 3 to block 5
        circuit.append("CZ", [35+i, 42+i]) # block 5 to block 6 (for last pattern)
    
    # IIIIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIZZZIIIIZZZIIII
    # Blocks 3,4,5,6 with qubits 0,1,2 in each
    for i in range(3):
        circuit.append("CZ", [21+i, 28+i]) # block 3 to block 4 (already added)
        circuit.append("CZ", [28+i, 35+i]) # block 4 to block 5
        circuit.append("CZ", [35+i, 42+i]) # block 5 to block 6
    
    return circuit

circuit = build_css_circuit()
print(f"\nCSS circuit has {len(circuit)} instructions")
print(circuit)
print(circuit)
