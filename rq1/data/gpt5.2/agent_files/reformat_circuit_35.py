import stim

def reformat():
    with open("circuit_35_generated.stim", "r") as f:
        content = f.read()
    
    circuit = stim.Circuit(content)
    
    with open("circuit_35_formatted.stim", "w") as f:
        for instruction in circuit:
            name = instruction.name
            targets = []
            for t in instruction.targets_copy():
                targets.append(str(t.value))
            
            args = ""
            if instruction.gate_args_copy():
                 args = "(" + ",".join(str(a) for a in instruction.gate_args_copy()) + ")"

            # Split targets into chunks of 10 pairs (20 targets) or just 10 targets
            # CX takes pairs, so we should be careful to split by pairs if it's a 2-qubit gate.
            # But single qubit gates can be split arbitrarily.
            # Let's just split by 10 targets for safety.
            
            chunk_size = 10
            # If it's a 2-qubit gate like CX, CZ, SWAP, etc. we must ensure we don't split a pair.
            # But wait, stim instructions for 2-qubit gates are just a list of targets.
            # If I have [t1, t2, t3, t4], it means (t1, t2) and (t3, t4).
            # So I should split in even numbers for 2-qubit gates.
            
            # Let's check the gate arity roughly.
            # Most 2-qubit gates: CX, CY, CZ, SWAP, ISWAP, etc.
            # We can check if name is in a known list or just always split by 2 if len > 1?
            # Actually, splitting by 10 is safe for both 1-qubit and 2-qubit gates (since 10 is even).
            # Unless there's a 3-qubit gate like CCZ... but stim doesn't decompose those into variable args usually?
            # Actually Stim doesn't support CCZ with variable args in the same way (it does support decomposition).
            # Stabilizer circuits only have 1 and 2 qubit gates.
            # So splitting by 10 is safe.
            
            for i in range(0, len(targets), chunk_size):
                chunk = targets[i:i+chunk_size]
                f.write(f"{name}{args} {' '.join(chunk)}\n")
            
if __name__ == "__main__":
    reformat()
