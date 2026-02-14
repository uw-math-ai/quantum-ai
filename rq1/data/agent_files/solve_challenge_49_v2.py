import stim
import sys

def solve():
    print("Reading stabilizers...")
    with open("stabilizers_49_v2.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))
        
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # We have 48 stabilizers for 49 qubits.
    # We need to find 1 more stabilizer to complete the set.
    # It must commute with all 48 and be independent.
    # However, stim.Tableau.from_stabilizers requires a full set of stabilizers.
    
    # Let's try to verify if stim has from_stabilizers
    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        print("Success! stim.Tableau.from_stabilizers accepted with allow_underconstrained=True.")
        c = t.to_circuit()
        
        # Stim's to_circuit() generates a circuit that maps |0> to the stabilizer state.
        # But for non-trivial tableaus it usually produces:
        # H, S, CX, etc.
        # Let's write it out.
        with open("circuit_attempt.stim", "w") as f:
            f.write(str(c))
        print("Circuit saved to circuit_attempt.stim")
        return
    except Exception as e:
        print(f"Direct conversion failed: {e}")
        
    # If that fails, we need to find the missing stabilizer.
    # We can try random Pauli strings.
    import random
    
    print("Searching for the 49th stabilizer...")
    num_qubits = 49
    
    # Check independence of the current set
    # We can use Gaussian elimination logic or just rely on stim's tableau logic if we can build it iteratively.
    
    # Brute force search for a commuting operator?
    # The space is 2^98, too big.
    # But we can solve for it.
    # The check matrix H is 48 x 98.
    # We want a vector v such that H * Symplectic * v = 0.
    # This is a linear algebra problem over GF(2).
    
    # Let's use a simpler approach:
    # Just try single qubit Z or X operators. One of them is likely to work if the code is not encoding that specific qubit.
    # Or, since we just need ONE valid completion, maybe we can just try to complete the tableau.
    
    # Using 'check_stabilizers_tool' is expensive, so we want to be sure.
    
    # Let's try to construct a Tableau from scratch using the stabilizers as Z output generators.
    # But we need the X output generators too (destabilizers).
    # This is hard to find manually.
    
    # Alternative:
    # Use stim.Tableau.from_stabilizers with 'allow_underconstrained=True' if it exists.
    # It seems from_stabilizers requires a full set.
    
    # Let's try adding Z_0, Z_1, ... until we find one that works.
    candidates = []
    for i in range(num_qubits):
        candidates.append(stim.PauliString("I"*i + "Z" + "I"*(num_qubits-1-i)))
        candidates.append(stim.PauliString("I"*i + "X" + "I"*(num_qubits-1-i)))
        
    for cand in candidates:
        # Check commutativity
        commutes = True
        for s in stabilizers:
            if not s.commutes(cand):
                commutes = False
                break
        if commutes:
            # Check independence
            # Try to form a tableau with this candidate added
            try:
                temp_stabs = stabilizers + [cand]
                t = stim.Tableau.from_stabilizers(temp_stabs)
                print(f"Found completing stabilizer: {cand}")
                c = t.to_circuit()
                with open("circuit_attempt.stim", "w") as f:
                    f.write(str(c))
                print("Circuit saved to circuit_attempt.stim")
                return
            except Exception as e:
                # Likely dependent
                pass

    print("Could not find a simple completing stabilizer.")

if __name__ == "__main__":
    solve()
