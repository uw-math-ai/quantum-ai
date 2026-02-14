import stim

def check():
    with open("target_stabilizers_124.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    paulis = [stim.PauliString(s) for s in stabs]
    
    print(f"Checking {len(paulis)} stabilizers...")
    
    for i in range(len(paulis)):
        for j in range(i+1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                print(f"Anticommute: {i} and {j}")
                print(f"{i}: {paulis[i]}")
                print(f"{j}: {paulis[j]}")
                # print the overlapping non-identity parts
                s1 = str(paulis[i])
                s2 = str(paulis[j])
                overlap = ""
                anticommutes = 0
                for k in range(len(s1)):
                    p1 = s1[k]
                    p2 = s2[k]
                    if p1 != '_' and p2 != '_':
                        if p1 != p2 and p1 != 'I' and p2 != 'I':
                            overlap += f"{k}:{p1}{p2} "
                            # XZ=-ZX, XY=iZ, etc.
                            # Two different Paulis anticommute.
                            anticommutes += 1
                print(f"Overlap details: {overlap}")
                print(f"Anticommutes count: {anticommutes}")
                # Print local neighborhood around overlap
                idx = int(overlap.split(':')[0])
                start = max(0, idx - 10)
                end = min(len(s1), idx + 15)
                print(f"Around {idx}:")
                print(f"19: {s1[start:end]}")
                print(f"86: {s2[start:end]}")
                return

if __name__ == "__main__":
    check()
