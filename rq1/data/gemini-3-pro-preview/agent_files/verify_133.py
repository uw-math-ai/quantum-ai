import stim
import sys

def verify_circuit(circuit_file, stabilizers_file):
    print(f'Verifying {circuit_file} against {stabilizers_file}')
    
    with open(circuit_file, 'r') as f:
        circ_text = f.read()
    
    c = stim.Circuit(circ_text)
    
    with open(stabilizers_file, 'r') as f:
        stabs = [l.strip() for l in f if l.strip()]
        
    print(f'Loaded {len(stabs)} stabilizers.')
    
    t = stim.Tableau.from_circuit(c)
    
    preserved = 0
    for s_str in stabs:
        s = stim.PauliString(s_str)
        # Check if s stabilizes the state T|0>
        # This is true if T_inv(s) stabilizes |0>
        # i.e. T_inv(s) is a product of Z_i operators with no -1 phase.
        
        t_inv = t.inverse()
        mapped = t_inv(s)
        
        # Check if mapped is only Zs and Is
        is_z = True
        for k in range(len(mapped)):
            p = mapped[k]
            if p == 1 or p == 2: # 1=X, 2=Y
                is_z = False
                break
        
        if is_z and mapped.sign == +1:
            preserved += 1
            
    print(f'Preserved: {preserved}/{len(stabs)}')

if __name__ == '__main__':
    verify_circuit('data/gemini-3-pro-preview/agent_files/circuit_133_clean.stim', 'data/gemini-3-pro-preview/agent_files/stabilizers_133.txt')

