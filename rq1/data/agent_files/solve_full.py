import stim

# The global stabilizers on 15 logical qubits
# We need to extract them from the file.
# They are lines 60-73 (0-indexed lines 61-74 in file, or just the last 14).

def get_logical_stabs():
    with open('stabilizers_75.txt') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    logical_stabs = []
    for line in lines[60:]:
        # Convert each 5-char block to 1 char
        l_stab = ""
        for i in range(15):
            block = line[i*5:(i+1)*5]
            if block == "IIIII": l_stab += "I"
            elif block == "XXXXX": l_stab += "X"
            elif block == "ZZZZZ": l_stab += "Z"
            else:
                # Should not happen based on previous analysis
                raise ValueError(f"Unknown block: {block}")
        logical_stabs.append(stim.PauliString(l_stab))
    return logical_stabs

logical_stabs = get_logical_stabs()
print("Logical stabilizers on 15 qubits:")
for s in logical_stabs:
    print(s)

# We have 14 stabilizers for 15 qubits.
# This leaves 1 degree of freedom.
# Let's fix the last logical qubit to Z (logical |0>).
# Or just use `from_stabilizers` and let it pick a state.
# But we need to make sure the state is valid.
# `from_stabilizers` will add Z stabilizers if underdetermined?
# No, it will pick a valid destabilizer for the missing one.
# But we want to output a valid state.
# We can just use the circuit from `from_stabilizers`.
# It will prepare a state stabilized by the given list.
# The remaining degree of freedom will be fixed arbitrarily (e.g. to +Z or +X).
# This is fine as long as it satisfies the provided stabilizers.

logical_circuit = stim.Tableau.from_stabilizers(logical_stabs).to_circuit()
print("\nLogical circuit:")
print(logical_circuit)

# Now we need to combine this with the encoding.
# The logical circuit acts on 15 qubits.
# We want to implement this on 75 qubits.
# Strategy:
# 1. Prepare 15 "seed" qubits in the state defined by `logical_circuit`.
#    We can map logical qubit i to physical qubit i*5 + 4 (the one that carries logical Z/X info in the block circuit).
#    Wait, in my block circuit, Z4 -> ZZZZZ and X4 -> XXXXX.
#    So qubit 4 of the block behaves like the logical qubit.
#    So if I prepare qubit 4 of each block in the correct state, and then run the "encoding" part?
    
#    Let's check the block circuit structure again.
#    It maps |00000> -> |0_L>.
#    So it maps Z4 -> Z_L.
#    And it maps X4 -> X_L (up to stabilizers).
#    So if I apply a gate G on qubit 4 before the encoding, 
#    it effectively applies logical G on the encoded state!
#    Example: 
#    Apply X on qubit 4 -> X_L on output.
#    Apply H on qubit 4 -> H_L on output?
#    Let's check.
#    H maps Z -> X, X -> Z.
#    So if I apply H on qubit 4, then Z4 becomes X4.
#    The encoding circuit maps X4 -> X_L.
#    So effectively I prepared a state stabilized by X_L (logical |+>).
#    Yes!
    
#    So the strategy is:
#    1. Initialize all 75 qubits to |0>.
#    2. Pick the "representative" qubits: 4, 9, 14, ..., 74. (Indices 4 + 5*i)
#    3. Apply the `logical_circuit` to these 15 representative qubits.
#       (We need to remap the indices in logical_circuit from 0..14 to 4, 9, ...).
#    4. Apply the "encoding" circuit to each block of 5 qubits.
#       The encoding circuit should be the one that maps |0000Z> to |0_L> (stabilized by Z_L) and |0000X> to |+_L> (stabilized by X_L).
#       Wait, my block circuit maps Z4 to Z_L and X4 to X_L.
#       So if I have a state |psi> on qubit 4, and |0> on 0..3,
#       applying the circuit yields Enc(|psi>).
#       Because the circuit maps Z4 -> Z_L and X4 -> X_L.
#       So linearity implies it maps the basis states correctly.
       
#    So the plan is solid:
#    1. Apply logical circuit on qubits {4, 9, ..., 74}.
#    2. Apply block encoding circuit on each block {5i, 5i+1, 5i+2, 5i+3, 5i+4}.
    
