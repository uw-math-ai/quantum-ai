import stim

def check_commutation():
    with open("stabilizers_49_v2.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = [stim.PauliString(s) for s in lines]
    all_commute = True
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Stabilizers {i} and {j} do not commute:")
                print(f"{lines[i]}")
                print(f"{lines[j]}")
                all_commute = False
                
    if all_commute:
        print("All stabilizers commute.")
    else:
        print("Some stabilizers do not commute.")

if __name__ == "__main__":
    check_commutation()
