import stim
import numpy as np

stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXIIIIIIIIIIIIIII",
    "XXXXXXXXXXXXXXXIIIIIIIIIIIIIIIXXXXXXXXXXXXXXX",
    "ZZZZZZZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "ZZZZZIIIIIZZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZZZZZZZZZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZZZZIIIIIZZZZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZZZZZZZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZZIIIIIZZZZZ"
]

def analyze_structure():
    n_qubits = len(stabilizers[0])
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {len(stabilizers)}")
    
    # Check for independent generators
    # We can use stim.Tableau.from_stabilizers but we need to handle the format
    # Stim expects Pauli strings. The input is already in that format.
    
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
        print(f"Tableau created successfully. Rank: {len(tableau)}")
    except Exception as e:
        print(f"Error creating tableau: {e}")

    # Let's count them and categorize
    blocks = 9
    block_size = 5
    
    print("Analyzing patterns...")
    
    # Check if they commute
    commutes = True
    for i in range(len(stabilizers)):
        for j in range(i+1, len(stabilizers)):
             s1 = stim.PauliString(stabilizers[i])
             s2 = stim.PauliString(stabilizers[j])
             if not s1.commutes(s2):
                 print(f"Non-commuting pair: {i}, {j}")
                 commutes = False
                 break
        if not commutes: break
    
    if commutes:
        print("All stabilizers commute.")
    
    # Try to find the missing stabilizer
    # We can use Gaussian elimination to find the kernel or just completion
    # But first, let's verify if we can make a tableau with allow_underconstrained=True
    
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        print("Tableau created with underconstrained=True")
        # Now we can just complete it?
        # A valid pure state must have 45 stabilizers.
        # We can try to add Z on each qubit and see if it commutes with everything and is independent
        
        # But wait, does the tableau object have a method to complete the stabilizers?
        # or we can just pick a state.
        
        # If we just want ANY state that satisfies the stabilizers, we can use the tableau to find one.
        # The tableau stores the stabilizers.
        # We can extract the circuit.
        
        # But we need a circuit that starts from |0>.
        # If we have a Tableau T that represents the state |psi>, then T|0> = |psi>.
        # So we want to find a Clifford C such that C|0> is a +1 eigenstate of all stabilizers.
        # This is exactly what Tableau.from_stabilizers gives us if fully constrained.
        # Since it is underconstrained, it might give us a mixed state or just a set of generators.
        
        # Let's see what happens if we add one more stabilizer to make it full rank.
        # We can iterate through all single-qubit Paulis and see if adding one makes it full rank.
        
        candidates = []
        for q in range(n_qubits):
            for p in ["X", "Z"]:
                s = ["I"] * n_qubits
                s[q] = p
                cand = "".join(s)
                # Check commutativity
                cand_ps = stim.PauliString(cand)
                if all(cand_ps.commutes(stim.PauliString(s)) for s in stabilizers):
                    # Check independence
                    # We can try to form a tableau
                    try:
                        stabs_plus = stabilizers + [cand]
                        t = stim.Tableau.from_stabilizers([stim.PauliString(x) for x in stabs_plus])
                        print(f"Found completing stabilizer: {cand}")
                        candidates.append(cand)
                        break # Found one
                    except:
                        pass
            if candidates: break
            
        if candidates:
            final_stabs = stabilizers + [candidates[0]]
            t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in final_stabs])
            circuit = t.to_circuit()
            print("Circuit generated!")
            with open("circuit.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Could not find a completing stabilizer.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_structure()
