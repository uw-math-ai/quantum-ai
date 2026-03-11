import stim
import sys
import os

input_path = "candidate_large.stim"
output_path = "candidate_fixed.stim"

def fix_circuit():
    with open(input_path, 'r') as f:
        content = f.read()
    
    # Simple string replacement might be dangerous if RX is used elsewhere, 
    # but here it's likely just the initialization.
    # Stim's graph state synthesis puts initialization at the beginning.
    
    # We'll parse it as a circuit to be safe, then iterate instructions.
    circuit = stim.Circuit(content)
    new_circuit = stim.Circuit()
    
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace RX with H
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        elif instruction.name == "TICK":
            continue
        else:
            new_circuit.append(instruction)
            
    with open(output_path, 'w') as f:
        f.write(str(new_circuit))
    print(f"Fixed circuit written to {output_path}")
    return str(new_circuit)

if __name__ == "__main__":
    fix_circuit()
