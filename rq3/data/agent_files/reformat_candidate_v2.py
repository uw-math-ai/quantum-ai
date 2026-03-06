import stim

def main():
    try:
        with open("candidate_clean.stim", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("candidate_clean.stim not found")
        return
    
    try:
        circuit = stim.Circuit(content)
    except Exception as e:
        print(f"Parse error: {e}")
        return

    with open("candidate_formatted.stim", "w") as f:
        for instruction in circuit:
            name = instruction.name
            gate_targets = instruction.targets_copy()
            
            # Helper to format target
            def fmt(t):
                # Simple integer targets
                return str(t.value)

            target_strs = [fmt(t) for t in gate_targets]
            
            if name in ["CX", "CNOT", "CZ", "SWAP", "ISWAP"]:
                # 2-qubit gates, targets are pairs.
                # Write each pair on a new line or grouped.
                # Grouping by 10 targets (5 pairs) seems reasonable.
                
                chunk_size = 10 
                # Ensure chunk_size is even for pair gates
                if chunk_size % 2 != 0: chunk_size += 1
                
                for i in range(0, len(target_strs), chunk_size):
                    chunk = target_strs[i:i+chunk_size]
                    if chunk:
                        f.write(f"{name} {' '.join(chunk)}\n")
            
            elif name in ["H", "S", "X", "Y", "Z", "RX", "RY", "RZ", "I"]:
                # Single qubit gates
                chunk_size = 20
                for i in range(0, len(target_strs), chunk_size):
                    chunk = target_strs[i:i+chunk_size]
                    if chunk:
                        f.write(f"{name} {' '.join(chunk)}\n")
            
            elif name == "TICK":
                pass # Skip ticks? Or preserve. Let's skip.
                
            else:
                # Other instructions
                f.write(str(instruction) + "\n")

    print("Reformatted circuit saved to candidate_formatted.stim")

if __name__ == "__main__":
    main()
