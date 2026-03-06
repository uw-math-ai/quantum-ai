import stim
import sys

def check():
    print("Checking commutativity...")
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\my_stabilizers.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabs = []
    for line in lines:
        try:
            stabs.append(stim.PauliString(line))
        except:
            pass

    bad_pairs = []
    for i in range(len(stabs)):
        for j in range(i + 1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                bad_pairs.append((i, j))
                print(f"Anticommute: {i} vs {j}")
                # Optional: print details
                # print(f"  {i}: {stabs[i]}")
                # print(f"  {j}: {stabs[j]}")

    print(f"Total anticommuting pairs: {len(bad_pairs)}")

if __name__ == "__main__":
    check()
