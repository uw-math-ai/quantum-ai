import stim

with open("target_stabilizers_114.txt") as f:
    lines = [l.strip() for l in f if l.strip()]

stabs = [stim.PauliString(l) for l in lines]

count = 0
for i in range(len(stabs)):
    for j in range(i+1, len(stabs)):
        if not stabs[i].commutes(stabs[j]):
            print(f"Non-commuting: {i} and {j}")
            # Find overlapping support
            # Print indices where they anti-commute
            anti = []
            for k in range(len(stabs[0])):
                if stabs[i][k] != 0 and stabs[j][k] != 0 and stabs[i][k] != stabs[j][k]:
                    anti.append(k)
            print(f"Overlap at: {anti}")
            count += 1
            if count > 5:
                print("Stopping early...")
                exit()
