import stim
import os

def generate():
    try:
        with open('my_stabilizers.txt', 'r') as f:
            content = f.read().replace('\n', '').strip()
        
        stabilizers = [s.strip() for s in content.split(',')]
        # Filter empty strings just in case
        stabilizers = [s for s in stabilizers if s]
        
        print(f"Loaded {len(stabilizers)} stabilizers")
        
        paulis = [stim.PauliString(s) for s in stabilizers]
        
        # Try graph state synthesis
        print("Synthesizing...")
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method='graph_state')
        
        # Process circuit to remove resets and map RX to H
        circuit_str = str(circuit)
        lines = circuit_str.split('\n')
        new_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle RX (reset X) -> H (initialize |0> to |+>)
            if line.startswith('RX'):
                targets = line[3:].split()
                # Split into chunks to avoid long lines
                chunk_size = 20
                for i in range(0, len(targets), chunk_size):
                    chunk = targets[i:i+chunk_size]
                    new_lines.append(f'H {" ".join(chunk)}')
            
            # Handle R/RZ (reset Z) -> Remove (already |0>)
            elif line.startswith('R ') or line.startswith('RZ '):
                pass
            # Handle TICK -> Remove (optional, but cleaner)
            elif line.startswith('TICK'):
                pass
            
            # Handle long standard gates
            else:
                parts = line.split()
                gate = parts[0]
                args = parts[1:]
                
                # If args are just integers (qubits), we can split
                # Check if it's a simple gate (1 or 2 qubit ops)
                # CZ takes pairs. X takes singles.
                
                if gate in ['H', 'X', 'Y', 'Z', 'S', 'S_DAG', 'SQRT_X', 'SQRT_X_DAG', 'SQRT_Y', 'SQRT_Y_DAG']:
                    chunk_size = 20
                    for i in range(0, len(args), chunk_size):
                        chunk = args[i:i+chunk_size]
                        new_lines.append(f'{gate} {" ".join(chunk)}')
                
                elif gate in ['CX', 'CZ', 'SWAP']:
                    # These take pairs. We must keep pairs together.
                    # args is a list of qubits. length must be even.
                    pairs = []
                    for i in range(0, len(args), 2):
                        pairs.append(f"{args[i]} {args[i+1]}")
                    
                    chunk_size = 10 # 10 pairs
                    for i in range(0, len(pairs), chunk_size):
                        chunk = pairs[i:i+chunk_size]
                        new_lines.append(f'{gate} {" ".join(chunk)}')
                
                else:
                    new_lines.append(line)
                
        final_circuit_str = '\n'.join(new_lines)
        
        out_path = 'candidate_opt.stim'
        with open(out_path, 'w') as f:
            f.write(final_circuit_str)
            
        print(f"Successfully generated {out_path}")
        print("First few lines:")
        print('\n'.join(new_lines[:10]))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    generate()
