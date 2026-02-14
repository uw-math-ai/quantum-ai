import stim
import sys
import os

def check():
    path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_114.txt"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Num lines: {len(lines)}")
    lengths = [len(l) for l in lines]
    print(f"Lengths: {min(lengths)} - {max(lengths)}")
    
    if min(lengths) != max(lengths):
        print("Error: inconsistent lengths")
        return

    num_qubits = lengths[0]
    print(f"Num qubits: {num_qubits}")
    
    # Check commutation
    ps = [stim.PauliString(l) for l in lines]
    
    all_commute = True
    for i in range(len(ps)):
        for j in range(i+1, len(ps)):
            if not ps[i].commutes(ps[j]):
                print(f"Anticommute: {i} and {j}")
                print(f"{lines[i]}")
                print(f"{lines[j]}")
                all_commute = False
                # break if you want just one

    
    if all_commute:
        print("All stabilizers commute.")
    else:
        print("Some stabilizers anticommute.")

if __name__ == "__main__":
    check()
