import stim

stabilizers_str = [
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

def solve():
    try:
        # Convert strings to Stim PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers_str]
        
        # Create a tableau from the stabilizers
        # allow_underconstrained=True because we might have fewer than N stabilizers
        # allow_redundant=True just in case
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # Synthesize a circuit that prepares this tableau from |00...0>
        # The 'elimination' method usually works well for stabilizer states
        circuit = tableau.to_circuit(method="elimination")
        
        print(circuit)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
