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
flag_qubits = []

for s_idx, stab in enumerate(stabilizers):
    flag = current_ancilla
    flag_qubits.append(flag)
    
    # Initialize ancilla
    # We assume it starts at |0> implicitly or we can reset it if reusing.
    # The prompt says "All ancilla qubits must be initialized in the |0> state".
    # Stim assumes |0> initially for unused qubits.
    
    # Standard measurement circuit for P:
    # H anc
    # For each qubit q involved in P:
    #   If P_q = X: CX anc q
    #   If P_q = Z: CZ anc q
    #   If P_q = Y: CY anc q (using Stim's CY gate)
    # H anc
    # M anc
    
    check_lines.append(f"H {flag}")
    
    for q_idx, p in enumerate(stab):
        if p == 'X':
            check_lines.append(f"CX {flag} {q_idx}")
        elif p == 'Z':
            check_lines.append(f"CZ {flag} {q_idx}")
        elif p == 'Y':
            # Stim supports CY? Yes.
            check_lines.append(f"CY {flag} {q_idx}")
            
    check_lines.append(f"H {flag}")
    check_lines.append(f"M {flag}")
    
    current_ancilla += 1

full_circuit = orig_circuit + "\n" + "\n".join(check_lines)

with open("gen_ft_v1.stim", "w") as f:
    f.write(full_circuit)

print(f"Generated gen_ft_v1.stim with {len(flag_qubits)} flags.")
# Output flags as a comma-separated list for easy copy-paste
print(f"FLAGS={','.join(map(str, flag_qubits))}")
