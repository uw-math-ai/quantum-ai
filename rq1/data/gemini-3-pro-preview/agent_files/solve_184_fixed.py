import stim

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    return [stim.PauliString(s) for s in lines]

def main():
    stabilizers = read_stabilizers('data/gemini-3-pro-preview/agent_files/stabilizers_184.txt')
    
    # Fix stabilizer 32
    # Original: XXXX__X__XX______X... (indices 0, 1, 2, 3, 6, 9, 10, 17)
    # New:      XXXX___X__XX______X... (indices 0, 1, 2, 3, 7, 10, 11, 18)
    
    new_s32 = stim.PauliString(184)
    # Reset to identity first
    
    # Indices to set to X
    indices = [0, 1, 2, 3, 7, 10, 11, 18]
    for idx in indices:
        new_s32[idx] = "X"
        
    stabilizers[32] = new_s32
    
    t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    c = t.to_circuit()
    
    print(c)

if __name__ == "__main__":
    main()
