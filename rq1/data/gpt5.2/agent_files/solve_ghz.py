import stim

def solve():
    # Target stabilizers
    # XXXXXX
    # ZZZZZZ
    
    # Let's try to construct a state that satisfies these.
    # A GHZ-like state might work?
    # |000000> + |111111> is stabilized by XXXXXX and Z_i Z_j. 
    # Wait, |GHZ> = |00...0> + |11...1>.
    # XXXXXX (|00...0> + |11...1>) = |11...1> + |00...0> = |GHZ>. (Stabilized)
    # ZZZZZZ (|00...0> + |11...1>) = (|00...0> + (-1)^6 |11...1>) = |00...0> + |11...1>. (Stabilized)
    
    # So the GHZ state on 6 qubits satisfies both.
    
    # Circuit for GHZ state on 6 qubits:
    # H 0
    # CX 0 1
    # CX 1 2
    # CX 2 3
    # CX 3 4
    # CX 4 5
    
    c = stim.Circuit()
    c.append("H", [0])
    for i in range(5):
        c.append("CX", [i, i+1])
        
    print(c)

if __name__ == "__main__":
    solve()
