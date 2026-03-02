import stim
import sys

def debug_verify():
    circuit_file = 'circuit_133_clean.stim'
    stabilizers_file = 'stabilizers_133.txt'
    
    with open(circuit_file, 'r') as f:
        circ_text = f.read()
    
    # Check for invalid lines
    lines = circ_text.splitlines()
    if len(lines) > 0 and 'Success' in lines[0]:
        print('Removing first line')
        circ_text = '\n'.join(lines[1:])
        
    c = stim.Circuit(circ_text)
    t = stim.Tableau.from_circuit(c)
    t_inv = t.inverse()
    
    with open(stabilizers_file, 'r') as f:
        stabs = [l.strip() for l in f if l.strip()]
        
    print(f'Loaded {len(stabs)} stabilizers.')
    
    for i in range(min(5, len(stabs))):
        s_str = stabs[i]
        try:
            s = stim.PauliString(s_str)
        except Exception as e:
            print(f'Error parsing stab {i}: {e}')
            continue
            
        mapped = t_inv(s)
        print(f'Stab {i}: {s_str[:20]}... -> Mapped: {mapped}')
        
        is_z = True
        for k in range(len(mapped)):
            p = mapped[k]
            if p == 1 or p == 2:
                is_z = False
                break
        print(f'Is Z product? {is_z}. Sign: {mapped.sign}')

if __name__ == '__main__':
    debug_verify()

