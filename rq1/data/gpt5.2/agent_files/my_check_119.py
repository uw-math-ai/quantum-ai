import stim

def check():
    with open("stabilizers_119.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    ps = [stim.PauliString(l) for l in lines]
    n = len(ps)
    print(f"Checking {n} stabilizers.")
    
    anticomms = 0
    for i in range(n):
        for j in range(i+1, n):
            if not ps[i].commutes(ps[j]):
                anticomms += 1
                if anticomms <= 5:
                    print(f"Anticommute: {i} vs {j}")
                    
    print(f"Total anticommuting pairs: {anticomms}")

if __name__ == "__main__":
    check()
