import stim

def debug_commutation():
    with open('target_stabilizers_rq3.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    s25 = stim.PauliString(lines[25])
    s52 = stim.PauliString(lines[52])
    
    print(f"S25: {s25}")
    print(f"S52: {s52}")
    
    print(f"S25 length: {len(s25)}")
    print(f"S52 length: {len(s52)}")
    
    commutes = s25.commutes(s52)
    print(f"Commutes: {commutes}")
    
    # Check overlapping non-identity
    for k in range(len(s25)):
        p25 = s25[k]
        p52 = s52[k]
        if p25 != 0 and p52 != 0:
            print(f"Overlap at {k}: {p25} vs {p52}")

if __name__ == "__main__":
    debug_commutation()
