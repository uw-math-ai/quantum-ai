import stim
import numpy as np

stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
]

def check_commutativity():
    n = len(stabilizers)
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
    # The above line might fail if they anti-commute.
    # So let's check manually.
    
    paulis = [stim.PauliString(s) for s in stabilizers]
    for i in range(n):
        for j in range(i+1, n):
            if not paulis[i].commutes(paulis[j]):
                print(f"Anticommutes: {i} and {j}")
                print(f"  {stabilizers[i]}")
                print(f"  {stabilizers[j]}")
                return False
    print("All stabilizers commute.")
    return True

if __name__ == "__main__":
    if check_commutativity():
        try:
            # Attempt to create a tableau and circuit
            # Note: allow_underconstrained=True is important if we have fewer than 30 independent stabilizers.
            # We have 26 stabilizers provided. 30 qubits. So it is underconstrained.
            t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
            c = t.to_circuit()
            print("Circuit generated successfully.")
            with open("circuit_30_qubits.stim", "w") as f:
                f.write(str(c))
        except Exception as e:
            print(f"Error generating circuit: {e}")
