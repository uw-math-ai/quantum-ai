import stim
import sys

def check_comm():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_171_new.txt', "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        stabs = [stim.PauliString(line) for line in lines]
        
        anticommuting = []
        for i in range(len(stabs)):
            for j in range(i+1, len(stabs)):
                if not stabs[i].commutes(stabs[j]):
                    anticommuting.append((i, j))
        
        print(f"Total stabilizers: {len(stabs)}")
        print(f"Found {len(anticommuting)} anticommuting pairs")
        for i, j in anticommuting[:10]:
            print(f"({i}, {j})")
            # Print indices of X and Z to see overlap
            s1 = stabs[i]
            s2 = stabs[j]
            overlap = []
            for k in range(len(s1)):
                p1 = s1[k]
                p2 = s2[k]
                if p1 and p2 and p1 != p2:
                    overlap.append(k)
            print(f"Overlap at indices: {overlap}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_comm()
