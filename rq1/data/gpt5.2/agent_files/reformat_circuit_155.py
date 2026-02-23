import stim

def reformat_circuit():
    with open("circuit_155.stim", "r") as f:
        content = f.read()
    
    # We can parse it with stim, then iterate instructions and print them with limit
    c = stim.Circuit(content)
    
    with open("circuit_155_formatted.stim", "w") as f:
        for instruction in c:
            if isinstance(instruction, stim.CircuitRepeatBlock):
                # We don't expect repeat blocks here, but just in case
                f.write(str(instruction) + "\n")
                continue
                
            name = instruction.name
            targets = instruction.targets_copy()
            args = instruction.gate_args_copy()
            
            # If no args, we can split targets
            if not args:
                # We can split into multiple instructions
                # But wait, CX takes pairs.
                # H, S, etc take singles.
                # MPP takes groups.
                
                # Check arity
                # H, S, X, Y, Z, I, ... arity 1
                # CX, CNOT, CZ, ... arity 2
                # SWAP ... arity 2
                # M ... arity 1 (usually)
                
                # We can check instruction.gate_target_count() ? No
                # We can check if it takes pairs.
                # Heuristic: split into chunks of say 10 targets (or 5 pairs)
                
                chunk_size = 10 # small enough to fit in line
                
                # We need to respect the gate arity.
                # stim.gate_data(name).arity ? No such API easily exposed?
                # Actually, we can use a try-catch or just keep it simple.
                # Most gates here are H, S, CX.
                
                is_two_qubit = name in ["CX", "CNOT", "CZ", "CY", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]
                step = 2 if is_two_qubit else 1
                
                # Check if it divides evenly
                if len(targets) % step != 0:
                    # Should not happen for valid circuit
                    print(f"Warning: {name} targets length {len(targets)} not divisible by step {step}")
                    f.write(str(instruction) + "\n")
                    continue
                
                num_ops_in_chunk = 10
                chunk_len = step * num_ops_in_chunk
                
                for i in range(0, len(targets), chunk_len):
                    chunk = targets[i : i + chunk_len]
                    sub_instr = stim.CircuitInstruction(name, chunk, args)
                    f.write(str(sub_instr) + "\n")
            else:
                # If args (like noisy gates), usually they are single gates or we shouldn't split?
                # For this problem, we have ideal Clifford gates, so no args expected (except maybe annotations).
                f.write(str(instruction) + "\n")

if __name__ == "__main__":
    reformat_circuit()
