import stim

def generate_circuit():
    c = stim.Circuit()
    
    # Original ops
    # CX 1 0 0 1 1 0
    c.append("CX", [1, 0, 0, 1, 1, 0])
    c.append("H", [0])
    c.append("CX", [0, 3, 0, 4])
    c.append("H", [1])
    c.append("CX", [1, 0, 1, 4, 1, 6])
    c.append("CX", [4, 2, 2, 4, 4, 2])
    c.append("CX", [5, 2, 6, 2])
    c.append("CX", [4, 3, 3, 4, 4, 3])
    c.append("H", [3])
    c.append("CX", [3, 5, 3, 6, 4, 5, 6, 4, 6, 5, 5, 6, 6, 5])
    
    # Check XIXIXIX (0, 2, 4, 6)
    # Ancilla 7. X-check.
    c.append("H", [7])
    c.append("CX", [7, 0, 7, 2, 7, 4, 7, 6])
    c.append("H", [7])
    
    # Check ZZIIZZI (0, 1, 4, 5)
    # Ancilla 8. Z-check.
    # CX data -> anc
    c.append("CX", [0, 8, 1, 8, 4, 8, 5, 8])
    
    # Measure flags
    c.append("M", [7, 8])
    
    return c

print(generate_circuit())
