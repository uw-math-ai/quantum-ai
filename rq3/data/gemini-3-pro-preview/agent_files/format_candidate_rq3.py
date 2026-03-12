import stim

def main():
    with open("candidate_rq3_new_v4.stim", "r") as f:
        content = f.read()
    
    # Parse to verify and also to let stim formatting handle it?
    # Stim's string conversion usually produces long lines.
    # We can manually tokenize and wrap.
    
    circuit = stim.Circuit(content)
    
    with open("candidate_rq3_formatted.stim", "w") as f:
        for instruction in circuit:
            if isinstance(instruction, stim.CircuitRepeatBlock):
                # This circuit shouldn't have loops
                f.write(str(instruction) + "\n")
            else:
                name = instruction.name
                targets = instruction.targets_copy()
                args = instruction.gate_args_copy()
                
                # Format: NAME args targets
                line = name
                for arg in args:
                    line += f"({arg})"
                
                for t in targets:
                    s = str(t)
                    if len(line) + len(s) + 1 > 80:
                        f.write(line + "\n")
                        line = name + " " + s # varying indentation? No, just repeat command? 
                        # Stim doesn't support splitting a single command across lines easily without repeating the name?
                        # Actually it does. "CX 0 1 \n 2 3" is NOT valid?
                        # Stim doc says: "Instructions are separated by newlines or semicolons."
                        # "Arguments are separated by spaces."
                        # It doesn't explicitly say a single instruction can span lines.
                        # BUT, we can split one large instruction into multiple instructions of the same type!
                        # CX 0 1 2 3 is equivalent to CX 0 1 \n CX 2 3.
                        # This is safe for Clifford gates.
                        pass
                
                # Better approach: split into small chunks
                # For 2-qubit gates, chunks of 2. For 1-qubit gates, chunks of many.
                
                if name in ["CX", "CZ", "SWAP", "ISWAP", "CXSWAP", "SWAPCX", "SQRT_XX", "SQRT_YY", "SQRT_ZZ", "MXX", "MYY", "MZZ"]:
                    arity = 2
                else:
                    arity = 1
                
                # Check if it has args. If so, we might not be able to split easily if it's a measurement?
                # The gates in this circuit are RX, CZ, X, Y, Z, S, H. None have args.
                
                chunk_size = 5 # gates per line
                
                # Targets list
                ts = targets
                
                # We consume 'arity' targets at a time
                if len(ts) % arity != 0:
                     print(f"Warning: {name} has {len(ts)} targets, not divisible by {arity}")
                
                # Group targets
                groups = [ts[i:i+arity] for i in range(0, len(ts), arity)]
                
                # Write groups in chunks
                current_chunk = []
                for g in groups:
                    current_chunk.extend(g)
                    if len(current_chunk) >= chunk_size * arity:
                        # Write this chunk
                        # e.g. H 0 1 2 3 4
                        t_strs = [str(t) for t in current_chunk]
                        f.write(f"{name} {' '.join(t_strs)}\n")
                        current_chunk = []
                
                if current_chunk:
                    t_strs = [str(t) for t in current_chunk]
                    f.write(f"{name} {' '.join(t_strs)}\n")

if __name__ == "__main__":
    main()
