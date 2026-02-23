import stim
import sys

def solve_flattened_robust():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_114.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    dropped = [38, 92]
    stabilizers = [stim.PauliString(lines[i]) for i in range(len(lines)) if i not in dropped]

    t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circuit = t.to_circuit()
    
    # Manually stringify to ensure short lines
    output_lines = []
    
    for instruction in circuit:
        if instruction.name in ["H", "S", "X", "Y", "Z", "I", "SQRT_X", "SQRT_Y", "SQRT_Z"]:
            for t in instruction.targets_copy():
                output_lines.append(f"{instruction.name} {t.value}")
        elif instruction.name in ["CX", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ", "CNOT"]:
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                output_lines.append(f"{instruction.name} {targets[i].value} {targets[i+1].value}")
        else:
            output_lines.append(str(instruction))
            
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_114_robust.stim', 'w') as f:
        f.write('\n'.join(output_lines))

solve_flattened_robust()
