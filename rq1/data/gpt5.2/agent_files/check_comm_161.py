
import stim

def check_comm():
    s1 = "XXXXIIIXIIXXIIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    s2 = "IZIIZIIZZZZZIIIIIIIIIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    
    p1 = stim.PauliString(s1)
    p2 = stim.PauliString(s2)
    
    commutes = p1.commutes(p2)
    print(f"Commutes: {commutes}")
    
    # Check explicitly
    anti_count = 0
    for i in range(len(s1)):
        c1 = s1[i]
        c2 = s2[i]
        if (c1 == 'X' and c2 == 'Z') or (c1 == 'Z' and c2 == 'X'):
            print(f"Index {i}: {c1} vs {c2} (ANTI)")
            anti_count += 1
        elif (c1 == 'Y' and c2 != 'Y') or (c1 != 'Y' and c2 == 'Y'):
             # handle Y...
             pass
             
    print(f"Anti-commuting positions: {anti_count}")

if __name__ == "__main__":
    check_comm()
