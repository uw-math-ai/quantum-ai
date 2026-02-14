import stim

def check_commutation():
    with open('target_stabilizers_119_new.txt', 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    stim_stabs = [stim.PauliString(s) for s in stabs]
    
    for i in range(len(stim_stabs)):
        for j in range(i + 1, len(stim_stabs)):
            if not stim_stabs[i].commutes(stim_stabs[j]):
                print(f"Stabilizer {i} anticommutes with {j}")
                print(f"{i}: {stabs[i]}")
                print(f"{j}: {stabs[j]}")
                return

if __name__ == "__main__":
    check_commutation()