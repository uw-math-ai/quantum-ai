import stim

def check_commutation():
    stabilizers = []
    with open("current_stabilizers.txt", "r") as f:
        for l in f:
            l = l.strip().replace(",", "")
            if l:
                stabilizers.append(stim.PauliString(l))
    
    conflict = False
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Stabilizers {i} and {j} anti-commute!")
                conflict = True
                if i < 3 and j < 3: # Limit output
                    print(f"{stabilizers[i]}")
                    print(f"{stabilizers[j]}")
    
    if not conflict:
        print("All stabilizers commute.")

if __name__ == "__main__":
    check_commutation()
