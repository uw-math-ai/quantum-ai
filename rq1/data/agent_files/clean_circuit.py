import stim

def solve():
    with open("stabilizers_kept.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    
    # allow_underconstrained=True
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circuit = tableau.to_circuit()
    
    # Convert to flattened circuit with one operation per line (mostly)
    # Stim's to_circuit() often batches operations like CX 0 1 2 3...
    # We can iterate and recreate.
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        # If it's a huge instruction, maybe split it?
        # Stim's string format handles it, but for display safety we might want to split.
        # But actually, just relying on one-instruction-per-line is safer than one-huge-line.
        # But `instruction` object might represent "CX 0 1 2 3 ... 100 101".
        # We can decompose it?
        name = instruction.name
        targets = instruction.targets_copy()
        args = instruction.gate_args_copy()
        
        # If it's a 2-qubit gate with many targets, we can split into pairs.
        # If it's 1-qubit gate, split into singles.
        
        # This is just for safer printing/copying, but verifying it is valid is important.
        # Actually, let's just write it to file and trust `read` won't wrap if I use `Get-Content` carefully or python read.
        # But the problem is *I* (the agent) need to see the output to copy it.
        # And the tool output window wraps.
        
        # So I'll split into smaller instructions.
        
        if name in ["CX", "CNOT", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ", "XCX", "XCY", "XCZ", "YCX", "YCY", "YCZ", "ZCX", "ZCY", "ZCZ"]:
             # 2 qubit gates
             for k in range(0, len(targets), 2):
                 new_circuit.append(name, targets[k:k+2], args)
        elif name in ["H", "S", "X", "Y", "Z", "I", "SQRT_X", "SQRT_Y", "SQRT_Z", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG", "C_XYZ", "C_ZYX"]:
             # 1 qubit gates
             for k in range(len(targets)):
                 new_circuit.append(name, [targets[k]], args)
        else:
             # Other gates (measurements, etc), keep as is or handle
             new_circuit.append(instruction)

    # Validate
    # Verify it still does the job
    sim1 = stim.TableauSimulator()
    sim1.do(circuit)
    t1 = sim1.current_inverse_tableau()
    
    sim2 = stim.TableauSimulator()
    sim2.do(new_circuit)
    t2 = sim2.current_inverse_tableau()
    
    if t1 != t2:
        print("Warning: decomposed circuit differs!")
    
    with open("circuit_clean.txt", "w") as f:
        # iterate and write lines
        for instruction in new_circuit:
            f.write(str(instruction) + "\n")

    print(f"Saved clean circuit to circuit_clean.txt with {len(new_circuit)} lines.")

if __name__ == "__main__":
    solve()
