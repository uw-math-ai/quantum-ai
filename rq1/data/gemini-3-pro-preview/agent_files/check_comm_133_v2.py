import stim

def check_comm():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    print(f"Number of stabilizers: {len(stabilizers)}")
    
    found = False
    for i, s1 in enumerate(stabilizers):
        for j, s2 in enumerate(stabilizers):
            if i >= j: continue
            p1 = stim.PauliString(s1)
            p2 = stim.PauliString(s2)
            if not p1.commutes(p2):
                print(f"Anticommute: {i} and {j}")
                # print(f"{i}: {s1}")
                # print(f"{j}: {s2}")
                found = True
                break
        if found: break

    if not found:
        print("All commute.")

if __name__ == "__main__":
    check_comm()
