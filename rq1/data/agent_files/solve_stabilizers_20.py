
import stim
import numpy as np

# Stabilizers from the prompt
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

num_qubits = 20

def solve_circuit():
    # Create a Tableau from the stabilizers
    # Since we have 18 stabilizers for 20 qubits, we need to complete the stabilizer set to 20 to define a pure state.
    # The prompt implies "the stabilizer state", but usually that implies a unique state.
    # If the stabilizers are underconstrained, any state stabilizing them is valid? 
    # Or maybe I should treat it as a code and just pick *a* logical state?
    # The tool `check_stabilizers_tool` usually checks if the output state is a +1 eigenstate of the provided stabilizers.
    # So if I pick an arbitrary logical state (e.g. logical |00>), it should pass.
    
    # Let's try to use stim.Tableau.from_stabilizers
    # It allows underconstrained systems if we pass allow_underconstrained=True
    
    pauli_stabs = [stim.PauliString(s) for s in stabilizers]
    try:
        t = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
        # Note: from_stabilizers returns a tableau T such that T(Z_k) = stabilizers[k].
        # So applying T to |0...0> prepares the state stabilized by stabilizers[0]...stabilizers[k-1] (and implicitly Z_k...Z_{n-1} mapped to logicals if underconstrained).
        circuit = t.to_circuit("elimination")
        print(circuit)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

if __name__ == "__main__":
    solve_circuit()
