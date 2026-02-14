import stim

def solve():
    with open('target_stabilizers_60.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Line 5:  {lines[5]}")
    print(f"Line 37: {lines[37]}")

    s5 = stim.PauliString(lines[5])
    s37 = stim.PauliString(lines[37])
    
    print(f"S5:  {s5}")
    print(f"S37: {s37}")
    
    print(f"Commutes: {s5.commutes(s37)}")

if __name__ == "__main__":
    solve()
