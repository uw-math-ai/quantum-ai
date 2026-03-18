import stim
import sys

def generate_circuit():
    with open('input.stim', 'r') as f:
        circuit_text = f.read()
    
    lines = circuit_text.strip().split('\n')
    new_lines = []
    
    ancilla = 28
    control_0_replaced = False
    
    for line in lines:
        parts = line.split()
        if not parts: continue
        gate = parts[0]
        try:
            args = [int(x) for x in parts[1:]]
        except:
            new_lines.append(line)
            continue
        
        if gate == 'CX' and len(args) >= 18 and args[0] == 0:
            # Check if it's the right block
            targets = args[1::2]
            controls = args[0::2]
            if all(c == 0 for c in controls):
                # Found it!
                new_lines.append(f'CX 0 {ancilla}')
                
                # The original CXs, but with ancilla as control
                new_args = []
                for t in targets:
                    new_args.extend([ancilla, t])
                new_lines.append(f'CX ' + ' '.join(str(x) for x in new_args))
                
                new_lines.append(f'CX 0 {ancilla}')
                
                control_0_replaced = True
                continue
        
        new_lines.append(line)
        
    if control_0_replaced:
        new_lines.append(f'M {ancilla}')
    else:
        print('WARNING: Did not find the block!')
        
    return '\n'.join(new_lines)

if __name__ == '__main__':
    circuit = generate_circuit()
    with open('attempt_1.stim', 'w') as f:
        f.write(circuit)
    print('Generated attempt_1.stim')
