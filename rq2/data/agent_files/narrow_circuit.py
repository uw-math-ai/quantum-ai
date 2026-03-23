import stim

def narrow_circuit():
    with open("candidate.stim", "r") as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    # Re-print with max line length or split instructions
    # We can decompose broadcast instructions
    # e.g. CX 0 1 2 3 -> CX 0 1 \n CX 2 3
    # H 0 1 -> H 0 \n H 1
    
    new_lines = []
    
    for op in circuit:
        name = op.name
        targets = op.targets_copy()
        
        # If no targets (e.g. TICK), just print
        if not targets:
            new_lines.append(str(op))
            continue
            
        # If many targets, split
        # How many per line?
        # Say 1 pair for 2-qubit gates, 1 for 1-qubit.
        
        if name in ["CX", "CZ", "SWAP"]:
            # 2 qubit gates. targets must be even.
            for i in range(0, len(targets), 2):
                t1 = targets[i].value
                t2 = targets[i+1].value
                new_lines.append(f"{name} {t1} {t2}")
        elif name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "M", "R"]:
            # 1 qubit gates (mostly). M and R can take many.
            # Split into individual
            for t in targets:
                new_lines.append(f"{name} {t.value}")
        else:
            # Other gates (MPP, etc). Just print as is, hope it's short.
            # For this task, we only used basic gates.
            new_lines.append(str(op))
            
    print("\n".join(new_lines))

if __name__ == "__main__":
    narrow_circuit()
