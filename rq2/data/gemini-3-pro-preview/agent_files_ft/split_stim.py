import sys

def split_stim(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        cmd = parts[0]
        args = parts[1:]
        
        # Single qubit gates
        if cmd in ['H', 'S', 'X', 'Y', 'Z', 'R', 'RX', 'M']:
            # Split into chunks of 10
            chunk_size = 10
            for i in range(0, len(args), chunk_size):
                chunk = args[i:i+chunk_size]
                new_lines.append(f"{cmd} {' '.join(chunk)}")
                
        # Two qubit gates
        elif cmd in ['CZ', 'CX', 'SWAP']:
            # Split into chunks of 10 pairs (20 args)
            # Args length must be even
            if len(args) % 2 != 0:
                print(f"Warning: {cmd} has odd number of args: {len(args)}")
                
            chunk_size = 20
            for i in range(0, len(args), chunk_size):
                chunk = args[i:i+chunk_size]
                new_lines.append(f"{cmd} {' '.join(chunk)}")
        
        # TICK
        elif cmd == 'TICK':
            new_lines.append("TICK")
            
        else:
            # Unknown or complex, keep as is
            new_lines.append(line)
            
    with open(output_file, 'w') as f:
        for line in new_lines:
            f.write(line + "\n")

if __name__ == "__main__":
    split_stim(sys.argv[1], sys.argv[2])
