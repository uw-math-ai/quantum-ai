import stim

circuit_str = """CX 15 0 0 15 15 0
H 7
CX 7 0 11 0 16 0 5 1 1 5 5 1
H 1 2 3 4 6 15
CX 1 2 1 3 1 4 1 6 1 7 1 13 1 15 1 16 7 2 2 7 7 2 2 7 2 11 2 16 3 2 7 3 3 7 7 3 3 10 3 16 4 6 4 7 4 11 4 12 4 13 4 15 15 5 5 15 15 5
H 15
CX 5 6 5 8 5 12 5 15 7 6 6 7 7 6 6 12 6 16 10 7 7 10 10 7 7 12 11 7 15 8 8 15 15 8 8 9 8 12 8 14 10 8 10 9 9 10 10 9 9 10 9 12 9 15 10 12 10 13 11 10 12 10 13 10 14 10 16 10 14 11 11 14 14 11 11 12 11 15 13 11 15 12 12 15 15 12 13 12 15 13 13 15 15 13 14 13 16 13 16 14"""

given_stabilizers = [
    "IIIIIXIIIXIXXIIII", "IIIIIIIIXIXIIXIXI", "IIIXIIIXIIIIIIXIX", "IIXIIIXIIIIIIIXIX", 
    "IIIIXXXXXIXXIIIIX", "IXIIXIIIIIXIIXIII", "IIIIIIIIXXIXIIIXI", "XIXXIIIIIIIIIIXII", 
    "IIIIIZIIIZIZZIIII", "IIIIIIIIZIZIIZIZI", "IIIZIIIZIIIIIIZIZ", "IIZIIIZIIIIIIIZIZ", "IIIIZZZZZIZZIIIIZ", "IZIIZIIIIIZIIZIII", "IIIIIIIIZZIZIIIZI", "ZIZZIIIIIIIIIIZII"
]

def to_binary(ps_str):
    if ps_str.startswith('+') or ps_str.startswith('-'):
        ps_str = ps_str[1:]
    vec = []
    for c in ps_str:
        if c in ['X', 'Y']:
            vec.append(1)
        else:
            vec.append(0)
    for c in ps_str:
        if c in ['Z', 'Y']:
            vec.append(1)
        else:
            vec.append(0)
    return vec

def solve():
    c = stim.Circuit(circuit_str)
    sim = stim.TableauSimulator()
    sim.do(c)
    
    canonical = sim.canonical_stabilizers()
    
    # Build basis for given stabilizers
    given_basis = []
    for s in given_stabilizers:
        r = to_binary(s)
        # Add to basis
        for b in given_basis:
            pivot = -1
            for k in range(len(b)):
                if b[k]:
                    pivot = k
                    break
            if r[pivot]:
                for k in range(len(r)):
                    r[k] = r[k] ^ b[k]
        if any(r):
            given_basis.append(r)
            
    print(f"Given stabilizers rank: {len(given_basis)}")
    
    # Find the extra one
    L = None
    for s in canonical:
        s_str = str(s)
        r = to_binary(s_str)
        r_orig = list(r)
        
        # Check against given basis
        for b in given_basis:
            pivot = -1
            for k in range(len(b)):
                if b[k]:
                    pivot = k
                    break
            if r[pivot]:
                for k in range(len(r)):
                    r[k] = r[k] ^ b[k]
                    
        if any(r):
            print(f"Found independent stabilizer L: {s_str}")
            L = s_str
            # Add to basis to find others if any
            given_basis.append(r_orig)
            
    if L is None:
        print("No independent stabilizer found? Impossible if dimension matches.")

if __name__ == "__main__":
    solve()
