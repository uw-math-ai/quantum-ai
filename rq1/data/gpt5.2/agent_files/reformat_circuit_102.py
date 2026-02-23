import stim

def reformat_circuit():
    with open(r"data\gemini-3-pro-preview\agent_files\circuit_102.stim", "r") as f:
        content = f.read()
        
    circuit = stim.Circuit(content)
    
    with open(r"data\gemini-3-pro-preview\agent_files\circuit_102_clean.stim", "w") as f:
        for instruction in circuit:
            # instruction is a stim.CircuitInstruction
            # We can print it.
            # But instruction might have many targets.
            # We should split it if it's too long?
            # Actually, just print it as is, stim formats it nicely usually.
            # But let's force 1 operation per line if possible?
            # No, instruction like CX 0 1 2 3 is one instruction.
            # We can decompose it into CX 0 1 \n CX 2 3
            
            name = instruction.name
            targets = instruction.targets_copy()
            args = instruction.gate_args_copy()
            
            if name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "H", "S", "X", "Y", "Z", "I", "M", "R", "RX", "RY", "RZ"]:
                # These gates can take multiple targets.
                # 1-qubit gates: 1 target per op
                # 2-qubit gates: 2 targets per op
                
                arity = 1
                if name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP"]:
                    arity = 2
                
                # Split into chunks of arity
                for i in range(0, len(targets), arity):
                    chunk = targets[i:i+arity]
                    # Format target: if it's a qubit, it's just integer.
                    # If it has modifiers (like lookback), it's stim.GateTarget
                    # We can use str(t)
                    
                    t_strs = []
                    for t in chunk:
                        if t.is_qubit_target:
                            t_strs.append(str(t.value))
                        elif t.is_x_target:
                             t_strs.append(f"X{t.value}")
                        # ... handle other types if needed, but for stabilizer circuits usually just qubits
                        else:
                            t_strs.append(str(t)) 
                            
                    f.write(f"{name} {' '.join(t_strs)}\n")
            else:
                # Other instructions (like TICK, SHIFT_COORDS), just write as is
                f.write(str(instruction) + "\n")

if __name__ == "__main__":
    reformat_circuit()
