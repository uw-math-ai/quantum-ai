
import stim

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
    "XXXXXXXXXXIIIIIXXXXXXXXXXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXXXXXXXXXXIIIIIXXXXXXXXXX",
    "IIIIIIIIIIXXXXXIIIIIIIIIIXXXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXXXXXIIIIIIIIIIXXXXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZZZZZZZZZIIIIIZZZZZZZZZZIIIII",
    "IIIIIZZZZZZZZZZIIIIIZZZZZZZZZZIIIIIIIIIIIIIII",
    "ZZZZZZZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZZZZZZZ"
]

print(f"Number of stabilizers: {len(stabilizers)}")
print(f"Length of stabilizers: {len(stabilizers[0])}")

def solve_circuit(stabilizers):
    # Try to find a tableau that has these stabilizers.
    # We need to fill the tableau to 45 stabilizers if it's less.
    # Or just use Tableau.from_stabilizers if it allows it.
    
    # Check if they commute first
    # Stim will throw error if they don't commute or have conflict.
    
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        print("Tableau created successfully.")
        
        # We want a circuit that prepares this state.
        # If we have N stabilizers for N qubits, to_circuit() prepares the state from |0>.
        # If underconstrained, it prepares a state in the +1 subspace.
        # But wait, does `to_circuit()` work for underconstrained?
        # Let's check.
        
        c = t.to_circuit()
        
        # The circuit from to_circuit() maps |00...0> to the stabilized state.
        # But we need to be careful: does it map the *stabilizers* correctly?
        # Yes, T * Z_i * T^-1 = S_i.
        # If we apply U_T to |0>, we get |psi> stabilized by S_i.
        
        # However, we must ensure that the initial state |0> is stabilized by Z_i.
        # If the tableau is underconstrained, stim might fill it with Z's for the remaining degrees of freedom.
        # This is fine, as long as the generated state satisfies our target stabilizers.
        
        print("Circuit generated.")
        return c
        
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return None

circuit = solve_circuit(stabilizers)
if circuit:
    with open("circuit_45.stim", "w") as f:
        f.write(str(circuit))
