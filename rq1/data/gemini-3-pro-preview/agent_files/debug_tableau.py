import stim
def debug():
    s_strs = ['XX', 'ZZ']
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in s_strs])
    print(f'Tableau maps Z0 to: {t.z_output(0)}')
    print(f'Tableau maps Z1 to: {t.z_output(1)}')
    
    c = t.to_circuit()
    print(f'Circuit: {c}')
    t2 = stim.Tableau.from_circuit(c)
    print(f'Circuit Tableau maps Z0 to: {t2.z_output(0)}')
    print(f'Circuit Tableau maps Z1 to: {t2.z_output(1)}')

if __name__ == '__main__':
    debug()

