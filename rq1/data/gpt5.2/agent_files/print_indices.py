import stim

def print_indices():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\my_stabilizers.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    indices_map = {}
    stabs = [stim.PauliString(s) for s in lines]
    
    # Check 30, 59, 86
    targets = [30, 59, 86]
    
    for i in targets:
        s = stabs[i]
        non_id = []
        for k in range(len(s)):
            p = s[k] # 0=I, 1=X, 2=Y, 3=Z
            if p != 0:
                p_char = "IXYZ"[p]
                non_id.append(f"{k}:{p_char}")
        print(f"Stabilizer {i}: {non_id}")

    # Check overlaps
    s30 = stabs[30]
    s59 = stabs[59]
    s86 = stabs[86]
    
    # 30 vs 59
    overlaps_30_59 = []
    for k in range(len(s30)):
        p30 = s30[k]
        p59 = s59[k]
        if p30 != 0 and p59 != 0:
            overlaps_30_59.append(f"{k}:({p30},{p59})")
            
    print(f"Overlap 30 vs 59: {overlaps_30_59}")
    # Commutativity check: if number of anti-commuting overlaps is odd, they anti-commute.
    # X(1) vs Z(3) => anti
    # Y(2) vs Z(3) => anti
    # X(1) vs Y(2) => anti
    # Same Pauli => commute
    
    # 30 vs 86
    overlaps_30_86 = []
    for k in range(len(s30)):
        p30 = s30[k]
        p86 = s86[k]
        if p30 != 0 and p86 != 0:
            overlaps_30_86.append(f"{k}:({p30},{p86})")
    
    print(f"Overlap 30 vs 86: {overlaps_30_86}")

if __name__ == "__main__":
    print_indices()
