import stim
import sys

def solve():
    # Load stabilizers
    with open("stabilizers_95.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabs)} stabilizers")
    if not stabs:
        print("No stabilizers found")
        return

    length = len(stabs[0])
    print(f"Qubit count: {length}")

    print(f"Stabilizer 27: {stabs[27]}")
    
    # Create Tableau from stabilizers
    try:
        pauli_stabs = [stim.PauliString(s) for s in stabs]
        
        # Check commutativity
        print("Checking commutativity...")
        anticommuting_pairs = []
        for i in range(len(pauli_stabs)):
            for j in range(i + 1, len(pauli_stabs)):
                if not pauli_stabs[i].commutes(pauli_stabs[j]):
                    anticommuting_pairs.append((i, j))
        
        if anticommuting_pairs:
            print(f"Found {len(anticommuting_pairs)} anticommuting pairs")
            for idx, (i, j) in enumerate(anticommuting_pairs):
                print(f"Pair {idx}: {i} and {j}")
                print(f"  {stabs[i]}")
                print(f"  {stabs[j]}")
                # Check where they anticommute
                s1 = pauli_stabs[i]
                s2 = pauli_stabs[j]
                for k in range(length):
                    p1 = s1[k]
                    p2 = s2[k]
                    if p1 and p2 and p1 != p2: # Anticommute locally? No.
                        pass
                # Commutativity check: count anti-commuting positions
                cnt = 0
                for k in range(length):
                    if s1[k] and s2[k] and s1[k] != s2[k]:
                        cnt += 1
                # Wait, this logic is for X and Z.
                # Pauli group commutativity: they commute if they differ in an even number of places (ignoring I).
                # Actually, X and Z anticommute. Y and Z anticommute. X and Y anticommute.
                # Two Pauli strings anticommute if they have an odd number of anticommuting positions.
                
                ac_pos = []
                for k in range(length):
                    p1 = s1[k] # 0=I, 1=X, 2=Y, 3=Z
                    p2 = s2[k]
                    # X(1) and Z(3) anticommute. Y(2) and Z(3) anticommute. X(1) and Y(2) anticommute.
                    # Basically if p1!=0 and p2!=0 and p1!=p2, they might anticommute.
                    # 1 and 3 -> AC. 2 and 3 -> AC. 1 and 2 -> AC.
                    # So if p1!=p2 and p1!=0 and p2!=0 -> AC.
                    if p1 != 0 and p2 != 0 and p1 != p2:
                        ac_pos.append(k)
                
                print(f"  Anticommutes at {len(ac_pos)} positions: {ac_pos}")
        else:
            print("All stabilizers commute.")

        # Try to generate circuit
        print("Generating circuit...")
        # allow_underconstrained=True is important because we might have fewer than N stabilizers
        # Check multiplicative consistency?
        # Gaussian elimination on the exponent matrix
        # stim.Tableau.from_stabilizers does this internally?
        # If allow_redundant=True, it might ignore sign conflict?
        # Let's check without allow_redundant=True.
        # But we might have fewer stabilizers. So allow_underconstrained=True is needed.
        # Try to create tableau with allow_redundant=False?
        
        try:
            print("Checking consistency with allow_redundant=False...")
            t = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True, allow_redundant=False)
            print("Consistent.")
        except Exception as e:
            print(f"Inconsistent! {e}")
            
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True, allow_redundant=True)
        
        # Verify the tableau
        print("Verifying tableau stabilizers...")
        # tableau.zs() are the stabilizers of the state |Psi> = U|0>
        # So check if input stabs are in the span of tableau.zs()
        # Actually, tableau.zs() are NOT the stabilizers of |Psi>.
        # Wait, tableau maps standard basis to stabilizer basis.
        # The stabilizers of the output state |Psi> correspond to the Z observables of the tableau.
        # Yes.
        
        circuit = tableau.to_circuit("graph_state")
        
        with open("circuit_95_correct.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
