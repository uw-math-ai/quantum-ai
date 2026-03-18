
import re

def parse_stim(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    operations = []
    for line in lines:
        if not line.strip(): continue
        # Handle comments
        if '#' in line: line = line.split('#')[0]
        if not line.strip(): continue
        
        parts = line.strip().split()
        name = parts[0]
        targets = []
        for p in parts[1:]:
            try:
                targets.append(int(p))
            except ValueError:
                pass 
        operations.append({'name': name, 'targets': targets})
    return operations

def flatten_ops(ops):
    flat_ops = []
    for op in ops:
        if op['name'] == 'CX':
            t = op['targets']
            for i in range(0, len(t), 2):
                flat_ops.append({'name': 'CX', 'targets': [t[i], t[i+1]]})
        elif op['name'] == 'H':
            t = op['targets']
            for i in range(len(t)):
                flat_ops.append({'name': 'H', 'targets': [t[i]]})
        else:
             flat_ops.append(op)
    return flat_ops

def optimize_circuit(ops):
    flat_ops = flatten_ops(ops)
    final_ops = []
    
    max_qubit = 0
    for op in flat_ops:
        for t in op.get('targets', []):
            if t > max_qubit: max_qubit = t
            
    next_flag = max_qubit + 1
    
    current_block = []
    current_control = -1
    
    for op in flat_ops:
        if op['name'] == 'CX':
            c, t = op['targets']
            if c == current_control:
                current_block.append(op)
            else:
                # Process previous block
                if current_block:
                    if len(current_block) >= 3:
                        process_block(current_block, final_ops, next_flag)
                        next_flag += 1
                    else:
                        final_ops.extend(current_block)
                
                current_block = [op]
                current_control = c
        else:
            # Process previous block
            if current_block:
                if len(current_block) >= 3:
                    process_block(current_block, final_ops, next_flag)
                    next_flag += 1
                else:
                    final_ops.extend(current_block)
            
            current_block = []
            current_control = -1
            final_ops.append(op)
            
    if current_block:
        if len(current_block) >= 3:
            process_block(current_block, final_ops, next_flag)
            next_flag += 1
        else:
            final_ops.extend(current_block)

    return final_ops, next_flag

def process_block(block, final_ops, flag_qubit):
    control = block[0]['targets'][0]
    # start flag
    final_ops.append({'name': 'CX', 'targets': [control, flag_qubit]})
    final_ops.extend(block)
    # end flag
    final_ops.append({'name': 'CX', 'targets': [control, flag_qubit]})

def ops_to_string(ops):
    lines = []
    for op in ops:
        targets = ' '.join(str(t) for t in op['targets'])
        lines.append(f'{op['name']} {targets}')
    return '\n'.join(lines)

ops = parse_stim('data/gemini-3-pro-preview/agent_files_ft/input.stim')
final_ops, next_flag = optimize_circuit(ops)
output_stim = ops_to_string(final_ops)

with open('data/gemini-3-pro-preview/agent_files_ft/attempt_1.stim', 'w') as f:
    f.write(output_stim)

print(f'Generated circuit with flags up to {next_flag-1}')

