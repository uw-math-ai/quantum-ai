import stim
import numpy as np

stabilizers = [
    "XZZXIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXX",
    "ZZZZZZZZZZZZZZZZZZZZ"
]

def check_commutativity(stabs):
    n = len(stabs)
    for i in range(n):
        for j in range(i + 1, n):
            s1 = stabs[i]
            s2 = stabs[j]
            anticommute = False
            # Check anticommutativity: count number of positions where paulis differ and are not I
            # X and Z anticommute. X and Y anticommute. Y and Z anticommute.
            # I and anything commute. Same paulis commute.
            count = 0
            for k in range(len(s1)):
                p1 = s1[k]
                p2 = s2[k]
                if p1 == 'I' or p2 == 'I' or p1 == p2:
                    continue
                count += 1
            
            if count % 2 == 1:
                print(f"Stabilizers {i} and {j} anticommute!")
                print(f"{i}: {s1}")
                print(f"{j}: {s2}")
                return False
    return True

print(f"Checking {len(stabilizers)} stabilizers for commutativity...")
if check_commutativity(stabilizers):
    print("All stabilizers commute.")
    
    # Try to solve using stim
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        circuit = tableau.to_circuit()
        print("Successfully generated circuit using stim.Tableau.from_stabilizers")
        print(circuit)
    except Exception as e:
        print(f"Failed to generate circuit: {e}")

else:
    print("Stabilizers do not commute.")
