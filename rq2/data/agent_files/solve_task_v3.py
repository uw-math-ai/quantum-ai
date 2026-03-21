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
    
    # Even for small groups, we might want to double-buffer if backprop is an issue?
    # But usually <4 is safe if no backprop.
    # However, to protect against X on Control spreading to >4, we MUST apply this to ANY control that hits >4 total.
    # The split_cnot_fanout logic splits into groups.
    # If total targets > 4, ALL groups must be protected?
    # Yes. Even a group of 1 must be protected if the control hits 10 others.
    # Because X on Control hits ALL groups.
    # If we double-buffer, X on Control hits t twice -> 0.
    # So we must double-buffer ALL chunks if the TOTAL degree is high.
    
    # We will assume split_cnot_fanout only calls this if total degree > 4?
    # Wait, split_cnot_fanout iterates over chunks.
    # I should pass a "needs_protection" flag?
    # Or just always double buffer if I split?
    # Yes, if I split, it implies high degree.
    # But split_cnot_fanout currently calls this for EACH chunk.
    # I will modify split_cnot_fanout to determine if high degree.
    
    # For now, I'll assume if generate_flagged_cnots is called with a group, we double buffer it.
    # UNLESS it's the "direct" path in previous code.
    # But I should remove the "direct" optimization if I want to suppress X_c.
    
    # Actually, split_cnot_fanout logic:
    # It chunks the targets.
    # If total targets <= 4, it calls generate... with all targets.
    # Inside generate..., if len <= 4, it did direct.
    # I should change that.
    
    # Wait, if total targets <= 4, X_c spreads to 4. Safe.
    # So direct is fine for small total.
    # If total > 4, we must double buffer ALL chunks.
    
    # So:
    
    # Use 2 ancillas per group
    ancilla1 = start_ancilla
    ancilla2 = start_ancilla + 1
    used_ancillas.extend([ancilla1, ancilla2])
    
    # Pass 1
    ops.append({'gate': 'CX', 'qubits': [control, ancilla1]})
    q_args1 = []
    for t in targets:
        q_args1.extend([ancilla1, t])
    ops.append({'gate': 'CX', 'qubits': q_args1})
    ops.append({'gate': 'CX', 'qubits': [control, ancilla1]})
    ops.append({'gate': 'M', 'qubits': [ancilla1]})
    
    # Pass 2
    ops.append({'gate': 'CX', 'qubits': [control, ancilla2]})
    q_args2 = []
    for t in targets:
        q_args2.extend([ancilla2, t])
    ops.append({'gate': 'CX', 'qubits': q_args2})
    ops.append({'gate': 'CX', 'qubits': [control, ancilla2]})
    ops.append({'gate': 'M', 'qubits': [ancilla2]})
            
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
            
            # Group pairs by control
            # But we must respect the order in the list?
            # Yes. But usually they are grouped.
            # "CX 0 3 0 13..."
            
            current_chunk = []
            current_control = -1
            
            # We need to look ahead to see total count for this control?
            # Or buffer them.
            
            # Buffer all pairs in this OP
            # Then process groups.
            
            # Simple grouping by consecutive control
            groups = []
            if pairs:
                curr = [pairs[0][1]]
                ctrl = pairs[0][0]
                for c, t in pairs[1:]:
                    if c == ctrl:
                        curr.append(t)
                    else:
                        groups.append((ctrl, curr))
                        curr = [t]
                        ctrl = c
                groups.append((ctrl, curr))
            
            for ctrl, targets in groups:
                if len(targets) <= 4:
                    # Direct
                    q_args = []
                    for t in targets:
                        q_args.extend([ctrl, t])
                    new_ops.append({'gate': 'CX', 'qubits': q_args})
                else:
                    # High degree! Apply double buffering to chunks
                    # Split into chunks
                    for i in range(0, len(targets), max_degree):
                        chunk = targets[i:i+max_degree]
                        generated_ops, used = generate_flagged_cnots(ctrl, chunk, max_degree, next_ancilla)
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
