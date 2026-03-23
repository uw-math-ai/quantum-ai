import stim
import sys

def main():
    try:
        circuit = stim.Circuit.from_file(r"data/gemini-3-pro-preview/agent_files_ft/input.stim")
        with open(r"data/gemini-3-pro-preview/agent_files_ft/chosen_stabilizers.txt", "r") as f:
            chosen_stabs = [line.strip() for line in f if line.strip()]
    except:
        circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input.stim")
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\chosen_stabilizers.txt", "r") as f:
            chosen_stabs = [line.strip() for line in f if line.strip()]

    num_qubits = 105
    ancilla_start = 105
    
    # Flatten to avoid long lines - manual decomposition
    flat_circuit = stim.Circuit()
    for op in circuit:
        if op.name in ["CX", "CY", "CZ", "SWAP"]:
            targets = op.targets_copy()
            for k in range(0, len(targets), 2):
                flat_circuit.append(op.name, [targets[k], targets[k+1]])
        elif op.name in ["H", "S", "X", "Y", "Z", "I", "M"]:
            targets = op.targets_copy()
            for t in targets:
                flat_circuit.append(op.name, [t])
        else:
            # Other gates like DETECTOR, OBSERVABLE, QUACK, etc.
            # Assuming simple circuit for now
            flat_circuit.append(op)
            
    final_circuit = flat_circuit.copy()
    
    ancilla_list = []
    
    for i, s_str in enumerate(chosen_stabs):
        anc = ancilla_start + i
        ancilla_list.append(anc)
        
        # Parse Pauli string
        # s_str is roughly "XIX..." length 105
        # We need to find non-identity indices
        
        # Init
        final_circuit.append("H", [anc])
        
        # Gates
        # To avoid creating too many gates, use targets list?
        # "CX anc target"
        # Since we use H-C-H, the control is always ancilla.
        # But Stim's CX is target-specific.
        # We can batch.
        
        # Collect targets for each type
        x_targets = []
        y_targets = []
        z_targets = []
        
        for q_idx, char in enumerate(s_str):
            if char == 'X':
                x_targets.append(q_idx)
            elif char == 'Y':
                y_targets.append(q_idx)
            elif char == 'Z':
                z_targets.append(q_idx)
                
        # Apply gates
        # CX anc -> X targets
        for t in x_targets:
            final_circuit.append("CX", [anc, t])
            
        # CY anc -> Y targets
        for t in y_targets:
            final_circuit.append("CY", [anc, t])
            
        # CZ anc -> Z targets
        for t in z_targets:
            final_circuit.append("CZ", [anc, t])
            
        # Finish
        final_circuit.append("H", [anc])
        final_circuit.append("M", [anc])
        
    print(f"Added {len(ancilla_list)} check gadgets.")
    
    # Save to file manually to avoid merging
    with open(r"data/gemini-3-pro-preview/agent_files_ft/candidate.stim", "w") as f:
        # Write original circuit decomposed
        for op in circuit:
            if op.name in ["CX", "CY", "CZ", "SWAP"]:
                targets = op.targets_copy()
                for k in range(0, len(targets), 2):
                    f.write(f"{op.name} {targets[k].value} {targets[k+1].value}\n")
            elif op.name in ["H", "S", "X", "Y", "Z", "I", "M"]:
                targets = op.targets_copy()
                for t in targets:
                    f.write(f"{op.name} {t.value}\n")
            else:
                f.write(str(op) + "\n")
                
        # Write check gadgets
        # Since we append to final_circuit previously, we need to replicate logic here or iterate final_circuit gadgets?
        # But final_circuit was merged.
        # We should just write gadgets here.
        ancilla_list = []
        for i, s_str in enumerate(chosen_stabs):
            anc = ancilla_start + i
            ancilla_list.append(anc)
            # Init
            f.write(f"H {anc}\n")
            
            x_targets = []
            y_targets = []
            z_targets = []
            for q_idx, char in enumerate(s_str):
                if char == 'X': x_targets.append(q_idx)
                elif char == 'Y': y_targets.append(q_idx)
                elif char == 'Z': z_targets.append(q_idx)
            
            for t in x_targets: f.write(f"CX {anc} {t}\n")
            for t in y_targets: f.write(f"CY {anc} {t}\n")
            for t in z_targets: f.write(f"CZ {anc} {t}\n")
            
            f.write(f"H {anc}\n")
            f.write(f"M {anc}\n")

    # Also save ancilla list
    with open(r"data/gemini-3-pro-preview/agent_files_ft/ancillas.txt", "w") as f:
        f.write(",".join(map(str, ancilla_list)))

if __name__ == "__main__":
    main()
