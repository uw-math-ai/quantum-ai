import stim
import sys

def check_commutativity(stabilizers):
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    for i in range(len(pauli_stabilizers)):
        for j in range(i + 1, len(pauli_stabilizers)):
            if not pauli_stabilizers[i].commutes(pauli_stabilizers[j]):
                print(f"Stabilizers {i} and {j} do not commute!")
                print(f"{stabilizers[i]}")
                print(f"{stabilizers[j]}")
                return False
    return True

def solve_circuit(stabilizers):
    # Create a Tableau from the stabilizers
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit("graph_state")
        return circuit
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return None

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

if check_commutativity(stabilizers):
    print("All stabilizers commute.")
    circuit = solve_circuit(stabilizers)
    if circuit:
        print(circuit)
    else:
        print("Failed to generate circuit")
else:
    print("Stabilizers do not commute.")
