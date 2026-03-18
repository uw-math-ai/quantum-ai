import re
import os

def parse_stim(content):
    lines = content.strip().split('\n')
    instructions = []
    for line in lines:
        line = line.strip()
        if not line: continue
        parts = line.split()
        gate = parts[0]
        qubits = [int(x) for x in parts[1:]]
        instructions.append({'gate': gate, 'qubits': qubits})
    return instructions

def analyze_structure(filename):
    print(f'Current working directory: {os.getcwd()}')
    print(f'Reading file: {filename}')
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f'File not found: {filename}')
        return

    print(f'File content length: {len(content)}')
    print(f'First 100 chars: {content[:100]}')
    
    instructions = parse_stim(content)
    
    # Analyze CX blocks
    flattened_ops = []
    for inst in instructions:
        if inst['gate'] == 'CX':
            qs = inst['qubits']
            for i in range(0, len(qs), 2):
                flattened_ops.append(('CX', qs[i], qs[i+1]))
        elif inst['gate'] == 'H':
            for q in inst['qubits']:
                flattened_ops.append(('H', q))
        else:
            pass # Ignore others

    # Identify consecutive CXs with same control
    blocks = []
    current_block = {'control': None, 'targets': [], 'start_idx': 0}
    
    for i, op in enumerate(flattened_ops):
        if op[0] == 'CX':
            ctrl, tgt = op[1], op[2]
            if current_block['control'] == ctrl:
                current_block['targets'].append(tgt)
            else:
                if current_block['control'] is not None:
                    current_block['end_idx'] = i - 1
                    blocks.append(current_block)
                current_block = {'control': ctrl, 'targets': [tgt], 'start_idx': i}
        else:
            if current_block['control'] is not None:
                current_block['end_idx'] = i - 1
                blocks.append(current_block)
            current_block = {'control': None, 'targets': [], 'start_idx': i}
            
    if current_block['control'] is not None:
        current_block['end_idx'] = len(flattened_ops) - 1
        blocks.append(current_block)
        
    high_fanout = [b for b in blocks if len(b['targets']) >= 2]
    
    print(f'Found {len(high_fanout)} high fan-out blocks.')
    for b in high_fanout:
        print(f'Control {b["control"]} targets {len(b["targets"])}: {b["targets"]}')

if __name__ == '__main__':
    analyze_structure('data/gemini-3-pro-preview/agent_files_ft/input_circuit.stim')
