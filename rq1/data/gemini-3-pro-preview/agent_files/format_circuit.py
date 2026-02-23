import stim
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
circuit_path = os.path.join(script_dir, 'circuit_119.stim')
output_path = os.path.join(script_dir, 'circuit_119_formatted.stim')

with open(circuit_path, 'r') as f:
    content = f.read()
    circuit = stim.Circuit(content)

with open(output_path, 'w') as f:
    for instruction in circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        args = instruction.gate_args_copy()
        
        if not args and targets:
            chunk_size = 6
            for i in range(0, len(targets), chunk_size):
                chunk = targets[i:i+chunk_size]
                temp_circuit = stim.Circuit()
                temp_circuit.append(name, chunk, args)
                f.write(str(temp_circuit).strip() + '\n')
        else:
            temp_circuit = stim.Circuit()
            temp_circuit.append(name, targets, args)
            f.write(str(temp_circuit).strip() + '\n')

print(f'Formatted circuit written to {output_path}')
