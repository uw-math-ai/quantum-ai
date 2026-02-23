import stim
import sys

def debug_verify():
    circuit_file = 'circuit_133.stim'
    stabilizers_file = 'stabilizers_133.txt'
    
    with open(circuit_file, 'r') as f:
        circ_text = f.read()
    
    c = stim.Circuit(circ_text)
    t = stim.Tableau.from_circuit(c)
    t_inv = t.inverse()
    
    with open(stabilizers_file, 'r') as f:
        stabs = [l.strip() for l in f if l.strip()]
        
    print(f'Loaded {len(stabs)} stabilizers.')
    
    preserved = 0
    for s_str in stabs:
        s = stim.PauliString(s_str)
        mapped = t_inv(s)
        
        is_z = True
        for k in range(len(mapped)):
            p = mapped[k]
            if p == 1 or p == 2:
                is_z = False
                break
        
        if is_z and mapped.sign == +1:
            preserved += 1
            
    print(f'Preserved: {preserved}/{len(stabs)}')

if __name__ == '__main__':
    debug_verify()

