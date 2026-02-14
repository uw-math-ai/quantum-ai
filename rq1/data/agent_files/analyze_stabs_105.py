import stim
import numpy as np

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def analyze_stabilizers():
    stabs = load_stabilizers('stabilizers_105.txt')
    num_stabs = len(stabs)
    lengths = [len(s) for s in stabs]
    print(f"Number of stabilizers: {num_stabs}")
    print(f"Lengths: {min(lengths)} - {max(lengths)}")
    if min(lengths) != max(lengths):
        print("Error: Stabilizers have different lengths!")
        return
    num_qubits = lengths[0]
    print(f"Number of qubits: {num_qubits}")

    # Check commutation
    # It's O(N^2 * M) where N is num stabs, M is num qubits. 
    # With 105 qubits and likely 105 stabilizers, this is small.
    
    # Using stim to check commutation is easy if we convert to Tableau or just check manually
    # But let's just use a simple check.
    
    def commute(s1, s2):
        # 0=I, 1=X, 2=Y, 3=Z
        # XZ = -YY, ZX = iY. Anti-commute if they share odd number of non-commuting pairs.
        # X and Z anti-commute. X and Y anti-commute. Y and Z anti-commute.
        # X and X commute.
        
        # Mapping: I->0, X->1, Y->2, Z->3
        map_pauli = {'I': 0, 'X': 1, 'Y': 2, 'Z': 3}
        
        anti_commutes = 0
        for i in range(len(s1)):
            p1 = s1[i]
            p2 = s2[i]
            if p1 == 'I' or p2 == 'I' or p1 == p2:
                continue
            anti_commutes += 1
            
        return (anti_commutes % 2) == 0

    print("Checking commutation...")
    all_commute = True
    for i in range(num_stabs):
        for j in range(i + 1, num_stabs):
            if not commute(stabs[i], stabs[j]):
                print(f"Stabilizers {i} and {j} do not commute!")
                all_commute = False
                break
        if not all_commute:
            break
            
    if all_commute:
        print("All stabilizers commute.")
    else:
        print("FAIL: Stabilizers do not commute.")

if __name__ == "__main__":
    analyze_stabilizers()
