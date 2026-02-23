import stim
import sys

def solve_flattened():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_114.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    dropped = [38, 92]
    stabilizers = [stim.PauliString(lines[i]) for i in range(len(lines)) if i not in dropped]

    t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circuit = t.to_circuit()
    
    # Flatten circuit
    flattened = stim.Circuit()
    for instruction in circuit:
        if instruction.name in ["H", "S", "X", "Y", "Z", "I", "SQRT_X", "SQRT_Y", "SQRT_Z"]:
            for t in instruction.targets_copy():
                flattened.append(instruction.name, [t])
        elif instruction.name in ["CX", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                flattened.append(instruction.name, [targets[i], targets[i+1]])
        else:
            flattened.append(instruction) # Keep others as is (e.g. TICK)
            
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_114_flat.stim', 'w') as f:
        f.write(str(flattened))

solve_flattened()
