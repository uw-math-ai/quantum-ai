import stim
import sys
import re

def parse_circuit(circuit_str):
    lines = [line.strip() for line in circuit_str.split('\n') if line.strip()]
    operations = []
    for line in lines:
        parts = line.split()
        gate = parts[0]
        try:
            qubits = [int(q) for q in parts[1:]]
        except ValueError:
            if '#' in line:
                line = line.split('#')[0]
                parts = line.split()
                if not parts: continue
                gate = parts[0]
                qubits = [int(q) for q in parts[1:]]
            else:
                continue
        operations.append({'gate': gate, 'qubits': qubits})
    return operations

def format_circuit(operations):
    lines = []
    for op in operations:
        q_str = ' '.join(str(q) for q in op['qubits'])
        lines.append(f"{op['gate']} {q_str}")
    return '\n'.join(lines)

def generate_flagged_cnots(control, targets, max_degree, start_ancilla):
    ops = []
    used_ancillas = []
    
    # If total targets is small, don't split.
    if len(targets) <= 4:
        q_args = []
        for t in targets:
            q_args.extend([control, t])
        ops.append({'gate': 'CX', 'qubits': q_args})
        return ops, []

    # Split targets into groups of size max_degree
    for i in range(0, len(targets), max_degree):
        group = targets[i:i+max_degree]
        
        # Use ancilla
        ancilla = start_ancilla + len(used_ancillas)
        used_ancillas.append(ancilla)
        
        # Op: CX control ancilla
        ops.append({'gate': 'CX', 'qubits': [control, ancilla]})
        
        # Op: CX ancilla targets
        q_args = []
        for t in group:
            q_args.extend([ancilla, t])
        ops.append({'gate': 'CX', 'qubits': q_args})
        
        # Op: CX control ancilla (uncompute)
        ops.append({'gate': 'CX', 'qubits': [control, ancilla]})
        
        # Op: Measure ancilla (M ancilla)
        ops.append({'gate': 'M', 'qubits': [ancilla]})
            
    return ops, used_ancillas

def split_cnot_fanout(operations, max_degree=3):
    new_ops = []
    max_qubit = 0
    for op in operations:
        if op['qubits']:
            max_qubit = max(max_qubit, max(op['qubits']))
    next_ancilla = max_qubit + 1
    flag_qubits = []

    for op in operations:
        if op['gate'] == 'CX':
            qubits = op['qubits']
            pairs = []
            for i in range(0, len(qubits), 2):
                pairs.append((qubits[i], qubits[i+1]))
            
            current_chunk = []
            current_control = -1
            
            for c, t in pairs:
                if c != current_control:
                    if current_chunk:
                        generated_ops, used = generate_flagged_cnots(current_control, current_chunk, max_degree, next_ancilla)
                        new_ops.extend(generated_ops)
                        flag_qubits.extend(used)
                        next_ancilla += len(used)
                    current_chunk = [t]
                    current_control = c
                else:
                    current_chunk.append(t)
            
            if current_chunk:
                 generated_ops, used = generate_flagged_cnots(current_control, current_chunk, max_degree, next_ancilla)
                 new_ops.extend(generated_ops)
                 flag_qubits.extend(used)
                 next_ancilla += len(used)

        else:
            new_ops.append(op)
            
    return new_ops, flag_qubits

if __name__ == "__main__":
    with open("baseline.stim", "r") as f:
        circuit_str = f.read()
    
    ops = parse_circuit(circuit_str)
    new_ops, flags = split_cnot_fanout(ops, max_degree=3)
    
    new_circuit = format_circuit(new_ops)
    
    with open("candidate.stim", "w") as f:
        f.write(new_circuit)
    
    print(f"FLAG_QUBITS: {flags}")
