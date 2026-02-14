import stim
import sys

def check_commutation():
    with open("target_stabilizers_138.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    print(f"Checking {len(stabs)} stabilizers for commutation...")
    
    # We can use stim.TableauSimulator() to check efficiently?
    # Or just iterate.
    
    for i in range(len(stabs)):
        for j in range(i + 1, len(stabs)):
            s1 = stim.PauliString(stabs[i])
            s2 = stim.PauliString(stabs[j])
            if not s1.commutes(s2):
                print(f"FAIL: Stab {i} and Stab {j} anti-commute!")
                print(f"Stab {i}: {stabs[i]}")
                print(f"Stab {j}: {stabs[j]}")
                return

    print("All stabilizers commute.")

if __name__ == "__main__":
    check_commutation()
