import stim

circuit_str = """CX 1 0 0 1 1 0
H 0 1 2 3 6 9
CX 0 1 0 2 0 3 0 6 0 9 0 12 0 14 0 15 0 16 0 20 0 21 0 22
H 4 5 10
CX 3 0 4 0 5 0 9 0 10 0 3 1 1 3 3 1
H 8
CX 1 5 1 6 1 8 1 9 1 10 1 11 1 13 1 14 1 15 1 19 1 20 2 1 3 1 4 1 8 1 9 1
H 7
CX 2 4 2 5 2 7 2 8 2 9 2 10 2 13 2 15 2 16 2 18 2 19 2 20 2 21 4 2 5 2 7 2 8 2 9 2 10 2 9 3 3 9 9 3 3 5 3 9 3 10 3 13 3 15 3 17 3 20 3 22 4 3 6 3 7 3 8 3 5 4 4 5 5 4 4 5 4 8 4 9 4 13 4 17 4 19 4 21 4 22 6 4 7 4 8 4 9 4 6 5 5 6 6 5 5 6 5 7 5 8 5 9 5 10 5 11 5 15 5 17 5 18 5 19 5 21 5 22 7 5 10 5 8 6 6 8 8 6 6 7 6 10 6 11 6 13 6 15 6 16 6 17 6 18 6 19 9 7 7 9 9 7 7 10 7 11 7 21 7 22 8 7 9 7 9 8 8 9 9 8 8 9 8 11 8 13 8 16 8 17 8 18 8 21 10 8 10 9 9 10 10 9 9 10 9 15 9 21 10 11 10 13 10 16 10 17 10 21 11 13 11 15 11 16 11 17 11 21 22 11 21 12 12 21 21 12 22 12 20 13 13 20 20 13 19 14 14 19 19 14 18 15 15 18 18 15 17 16 16 17 17 16 22 16 22 17 22 18 22 20"""

target_stabilizer = "XXXXIIXIIXXIIIIIIXIIII"
circuit = stim.Circuit(circuit_str)
pauli = stim.PauliString(target_stabilizer)

print(f"Circuit num_qubits: {circuit.num_qubits}")
# Pad pauli if necessary
if len(pauli) < circuit.num_qubits:
    pauli = stim.PauliString(str(pauli) + "_" * (circuit.num_qubits - len(pauli)))

print(f"Initial: {pauli}")

# Iterate backwards
for i in range(len(circuit) - 1, -1, -1):
    op = circuit[i]
    targets = op.targets_copy()
    # Reverse targets for proper inverse order
    targets.reverse()
    
    # Create a new instruction with reversed targets
    # We need to reconstruct the instruction
    # op.name gives the name (e.g. "CX")
    # op.gate_args_copy() gives args (e.g. for rotations)
    
    step_circ = stim.Circuit()
    step_circ.append(op.name, targets, op.gate_args_copy())
    
    pauli = pauli.after(step_circ)
    
    # Check if we have only Z and I
    s = str(pauli)
    # The string starts with sign (+ or -).
    has_non_z = False
    for char in s[1:]: # skip sign
        if char == 'X' or char == 'Y':
            has_non_z = True
            break
    
    # Print only if non-Z components exist (to reduce noise, but here we want to see when it cleans up)
    # Actually, we want to see when it becomes PURE Z/I.
    # Initially it is X.
    # At the end (start of circuit) it should be Z/I.
    
    print(f"Step {i}: {op.name} -> {pauli}")
    
