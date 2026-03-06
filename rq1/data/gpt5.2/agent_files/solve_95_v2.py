import stim
import os
import sys

def solve():
    input_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_95.txt'
    output_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_95_v2.stim'
    
    with open(input_path, 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Check commutativity
    pauli_strings = [stim.PauliString(s) for s in stabilizers]
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not pauli_strings[i].commutes(pauli_strings[j]):
                print(f"Stabilizers {i} and {j} anticommute!")
                return

    print("All stabilizers commute.")
    
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        
        with open(output_path, 'w') as f:
            for instruction in circuit:
                # Iterate over targets and print individual instructions
                name = instruction.name
                targets = instruction.targets_copy()
                args = instruction.gate_args_copy()
                
                # For 2-qubit gates like CX, targets are pairs.
                # For 1-qubit gates, targets are singles.
                # But stim handles varying number of targets for many gates.
                
                # To be safe and simple: just print one instruction per target (or pair)
                # But CX takes pairs.
                
                # Let's just print the instruction as is, but if it's too long, split it manually in string form?
                # No, better to use python logic.
                
                # Simpler approach:
                # If targets list is long, split it.
                if len(targets) > 5:
                   # For CX, we need even number of targets per split.
                   # For everything else, we can split arbitrarily?
                   # Most gates in tableau decomposition are 1-qubit or 2-qubit.
                   step = 2 if name in ["CX", "CNOT", "CZ", "SWAP"] else 1
                   # Actually, if we just split by 2, it works for 1-qubit gates too (2 targets = 2 ops).
                   # So split by 2 is safe for everything except multi-qubit gates like MPP?
                   # Tableau decomposition uses H, S, CX, X, Y, Z. All are 1 or 2 qubit.
                   
                   # So splitting by 2 is safe.
                   for i in range(0, len(targets), 2):
                       chunk = targets[i:i+2]
                       # Create a small circuit for just this instruction
                       temp_circ = stim.Circuit()
                       temp_circ.append(name, chunk, args)
                       f.write(str(temp_circ)) # This adds a newline
                else:
                    temp_circ = stim.Circuit()
                    temp_circ.append(name, targets, args)
                    f.write(str(temp_circ))
            
        print(f"Successfully generated circuit at {output_path}")
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
