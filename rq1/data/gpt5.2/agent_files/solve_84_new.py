import stim
import sys

def check_commutativity(stabilizers):
    num_stabilizers = len(stabilizers)
    num_qubits = len(stabilizers[0])
    print(f"Number of stabilizers: {num_stabilizers}")
    print(f"Number of qubits: {num_qubits}")

    anticommuting_pairs = []
    
    # Simple symplectic check
    # X = 1, Z = 2, Y = 3
    # A, B commute if bitwise: popcount( (x1*z2 + z1*x2) ) % 2 == 0
    
    def to_symplectic(s):
        xs = [1 if c in 'XY' else 0 for c in s]
        zs = [1 if c in 'ZY' else 0 for c in s]
        return xs, zs

    symp = [to_symplectic(s) for s in stabilizers]

    for i in range(num_stabilizers):
        for j in range(i + 1, num_stabilizers):
            x1, z1 = symp[i]
            x2, z2 = symp[j]
            
            comm = 0
            for k in range(num_qubits):
                if (x1[k] and z2[k]) != (z1[k] and x2[k]):
                    comm += 1
            
            if comm % 2 != 0:
                anticommuting_pairs.append((i, j))

    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} vs {j}")
            # print(f"    {stabilizers[i]}")
            # print(f"    {stabilizers[j]}")
        return False
    else:
        print("All stabilizers commute.")
        return True

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    return lines

if __name__ == "__main__":
    stabs = load_stabilizers("stabilizers_84_new.txt")
    if check_commutativity(stabs):
        try:
            tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabs], allow_underconstrained=True)
            print("Successfully created tableau from stabilizers.")
            circuit = tableau.to_circuit()
            print("Successfully generated circuit.")
            with open("circuit_84_new.stim", "w") as f:
                f.write(str(circuit))
        except Exception as e:
            print(f"Error creating tableau: {e}")
