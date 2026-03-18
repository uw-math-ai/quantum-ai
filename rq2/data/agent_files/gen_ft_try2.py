import sys

# Original circuit
with open("input_circuit.stim", "r") as f:
    orig_circuit = f.read().strip()

stabilizers = [
    "XXXIIIXXXIII", 
    "IIXXXIIIXXXI", 
    "XIIIXXXIIIXX", 
    "XXXXXXIIIIII", 
    "IIIIIIXXXXXX", 
    "IIZZZZIZIZII", 
    "ZIIIZIZZZIIZ", 
    "ZZZIIZZIIIZI", 
    "ZIIZZZIIZIZI", 
    "IZZIIIZZIZIZ"
]

check_lines = []
ancilla_start = 12
current_ancilla = ancilla_start
meas_qubits = []
flag_qubits = []

# For each stabilizer
for s_idx, stab in enumerate(stabilizers):
    # Main measurement ancilla
    meas_anc = current_ancilla
    current_ancilla += 1
    meas_qubits.append(meas_anc)
    
    # Identify active qubits in stabilizer
    active_indices = []
    for q_idx, p in enumerate(stab):
        if p in ['X', 'Z', 'Y']:
            active_indices.append((q_idx, p))
            
    # Init meas ancilla
    check_lines.append(f"H {meas_anc}")
    
    # Iterate interactions with interleaved flags
    for i, (q_idx, p) in enumerate(active_indices):
        # Interaction
        if p == 'X':
            check_lines.append(f"CX {meas_anc} {q_idx}")
        elif p == 'Z':
            check_lines.append(f"CZ {meas_anc} {q_idx}")
        elif p == 'Y':
            check_lines.append(f"CY {meas_anc} {q_idx}")
        
        # Add flag check after interaction if not the last one
        if i < len(active_indices) - 1:
            flag_anc = current_ancilla
            current_ancilla += 1
            flag_qubits.append(flag_anc)
            
            # Check if meas_anc has X error
            # If meas_anc has X, CX meas_anc flag_anc -> flag_anc has X.
            check_lines.append(f"CX {meas_anc} {flag_anc}")
            
    # Finalize measurement of meas_anc
    check_lines.append(f"H {meas_anc}")
    check_lines.append(f"M {meas_anc}")

# Add measurements for all flag ancillas (they were not measured yet)
for f in flag_qubits:
    check_lines.append(f"M {f}")

full_circuit = orig_circuit + "\n" + "\n".join(check_lines)

with open("gen_ft_try2.stim", "w") as f:
    f.write(full_circuit)

# Print flags for use in validate_circuit
# We need to pass ALL ancillas as "flag_qubits" because they are flags/ancillas.
# The tool expects `flag_qubits` list.
all_ancillas = meas_qubits + flag_qubits
print(f"FLAGS={','.join(map(str, all_ancillas))}")
print(f"Generated gen_ft_try2.stim with {len(all_ancillas)} ancillas.")
