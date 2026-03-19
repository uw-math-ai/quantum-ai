import stim

def generate_circuit():
    c = stim.Circuit()
    
    # Original ops
    # CX 1 0 0 1 1 0
    c.append("CX", [1, 0, 0, 1, 1, 0])
    
    # Check Z on 0, 1 (should be |0>)
    # Using ancillas 7, 8
    # Ancillas init |0>
    c.append("CX", [0, 7])
    c.append("CX", [1, 8])
    
    c.append("H", [0])
    
    # Check X on 0 (should be |+>)
    # Using ancilla 9
    c.append("H", [9])
    c.append("CX", [9, 0])
    c.append("H", [9])
    
    c.append("CX", [0, 3, 0, 4])
    c.append("H", [1])
    c.append("CX", [1, 0, 1, 4, 1, 6])
    
    # SWAP 2 4
    # CX 4 2 2 4 4 2
    c.append("CX", [4, 2, 2, 4, 4, 2])
    
    # Check Z on 4 (should be |0>)
    # Using ancilla 10
    c.append("CX", [4, 10])
    
    # CX 5 2 6 2
    c.append("CX", [5, 2, 6, 2])
    
    # SWAP 3 4
    # CX 4 3 3 4 4 3
    c.append("CX", [4, 3, 3, 4, 4, 3])
    
    # Check Z on 4 (should be |0>)
    # Using ancilla 11
    c.append("CX", [4, 11])
    
    c.append("H", [3])
    c.append("CX", [3, 5, 3, 6, 4, 5, 6, 4, 6, 5, 5, 6, 6, 5])
    
    # Measure flags
    c.append("M", [7, 8, 9, 10, 11])
    
    return c

print(generate_circuit())
