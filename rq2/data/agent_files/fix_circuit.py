import stim

def fix_circuit():
    c = stim.Circuit.from_file('input.stim')
    new_circuit = stim.Circuit()
    
    cx_buffer = []
    
    def flush_buffer(target_circuit, buffer, next_ancilla):
        if not buffer:
            return next_ancilla, []
        
        cleaned_ops = []
        i = 0
        while i < len(buffer):
            matched = False
            if i + 2 < len(buffer):
                p1 = buffer[i]
                p2 = buffer[i+1]
                p3 = buffer[i+2]
                if p1[0] == p3[0] and p1[1] == p3[1] and p2[0] == p1[1] and p2[1] == p1[0]:
                    cleaned_ops.append(('SWAP', p1[0], p1[1]))
                    i += 3
                    matched = True
            if not matched:
                cleaned_ops.append(('CX', buffer[i][0], buffer[i][1]))
                i += 1
        
        j = 0
        ancillas_to_measure = []
        
        while j < len(cleaned_ops):
            op = cleaned_ops[j]
            if op[0] == 'SWAP':
                target_circuit.append('SWAP', [op[1], op[2]])
                j += 1
                continue
            
            control = op[1]
            block = [op[2]]
            k = j + 1
            while k < len(cleaned_ops):
                next_op = cleaned_ops[k]
                if next_op[0] == 'CX' and next_op[1] == control:
                    block.append(next_op[2])
                    k += 1
                else:
                    break
            
            if len(block) > 7:
                targets = block
                chunk_size = 7
                for m in range(0, len(targets), chunk_size):
                    chunk = targets[m:m+chunk_size]
                    anc = next_ancilla
                    next_ancilla += 1
                    ancillas_to_measure.append(anc)
                    
                    target_circuit.append('CX', [control, anc])
                    cx_args = []
                    for t in chunk:
                        cx_args.extend([anc, t])
                    target_circuit.append('CX', cx_args)
                    target_circuit.append('CX', [control, anc])
            else:
                cx_args = []
                for t in block:
                    cx_args.extend([control, t])
                target_circuit.append('CX', cx_args)
            
            j = k
            
        return next_ancilla, ancillas_to_measure

    final_ancillas = []
    current_ancilla = c.num_qubits
    
    for instr in c:
        if instr.name == 'CX':
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                cx_buffer.append((targets[k].value, targets[k+1].value))
        else:
            current_ancilla, new_ancs = flush_buffer(new_circuit, cx_buffer, current_ancilla)
            final_ancillas.extend(new_ancs)
            cx_buffer = []
            new_circuit.append(instr)
            
    current_ancilla, new_ancs = flush_buffer(new_circuit, cx_buffer, current_ancilla)
    final_ancillas.extend(new_ancs)
    
    if final_ancillas:
        new_circuit.append('M', final_ancillas)
        
    new_circuit.to_file('candidate.stim')
    print('Fixed circuit generated.')

if __name__ == '__main__':
    fix_circuit()
