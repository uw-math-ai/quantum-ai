
import stim
import sys

# Load inputs
with open(r'input_circuit.stim', 'r') as f:
    circuit_text = f.read().strip()
with open(r'stabilizers.txt', 'r') as f:
    stabs = [line.strip().replace(',','') for line in f if line.strip()]

output_circuit = circuit_text + '\n'
ancilla_start = 30
flag_qubits = []

for idx, s in enumerate(stabs):
    anc = ancilla_start + idx
    flag_qubits.append(anc)
    
    # H anc
    output_circuit += f'H {anc}\n'
    
    # Controlled Paulis
    for q, p in enumerate(s):
        if p == 'X':
            output_circuit += f'CX {anc} {q}\n'
        elif p == 'Z':
            output_circuit += f'CZ {anc} {q}\n'
        elif p == 'Y':
            output_circuit += f'CY {anc} {q}\n'
            
    # H anc
    output_circuit += f'H {anc}\n'
    # Measure
    output_circuit += f'M {anc}\n'

with open('gen_ft_v1.stim', 'w') as f:
    f.write(output_circuit)

with open('ancillas.txt', 'w') as f:
    f.write(','.join(map(str, flag_qubits)))
