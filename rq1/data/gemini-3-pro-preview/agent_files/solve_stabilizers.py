import stim
import numpy as np
import galois

stabilizers_str = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXIIXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXIIXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXIIXXI",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIIXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXX",
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIIZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIZZI",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIIZZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZZZ",
    "XXXIIIIXXXIIIIXXXIIIIXXXIIII",
    "ZZZIIIIZZZIIIIZZZIIIIZZZIIII"
]

num_qubits = 28

# Helper to convert string to Pauli object
def str_to_pauli(s):
    return stim.PauliString(s)

# Create a Tableau from the stabilizers.
# We need to fill it up to 28 stabilizers.
# We can try adding Z_i for i in 0..27 and see which ones are independent and commute.
# But actually, we just need ANY 2 operators that commute with all 26 and are independent of them and each other.
# We can find them by looking at the null space of the commutation matrix?
# Or just random sampling.

current_stabilizers = [str_to_pauli(s) for s in stabilizers_str]

def commutes(p1, p2):
    return p1.commutes(p2)

def is_independent(candidates):
    # Check if a set of PauliStrings are independent.
    # We can use Gaussian elimination.
    if not candidates:
        return True
    
    mat = []
    for p in candidates:
        row = []
        for k in range(len(p)):
            # X, Z representation
            # I: 00, X: 10, Z: 01, Y: 11
            # We map to 2*n bits
            x = 1 if p[k] in [1, 3] else 0 # 1=X, 3=Y
            z = 1 if p[k] in [2, 3] else 0 # 2=Z, 3=Y
            row.extend([x, z])
        mat.append(row)
    
    gf_mat = galois.GF(2)(mat)
    rank = np.linalg.matrix_rank(gf_mat)
    return rank == len(candidates)

# Try to add single qubit Z operators
candidates_to_add = []
for i in range(num_qubits):
    s = ['I'] * num_qubits
    s[i] = 'Z'
    p = stim.PauliString("".join(s))
    
    # Check commutation with all existing
    if all(commutes(p, existing) for existing in current_stabilizers):
        # Check independence
        if is_independent(current_stabilizers + candidates_to_add + [p]):
            candidates_to_add.append(p)
            if len(current_stabilizers) + len(candidates_to_add) == num_qubits:
                break

if len(current_stabilizers) + len(candidates_to_add) < num_qubits:
    # Try X operators
    for i in range(num_qubits):
        s = ['I'] * num_qubits
        s[i] = 'X'
        p = stim.PauliString("".join(s))
        
        if all(commutes(p, existing) for existing in current_stabilizers):
            if is_independent(current_stabilizers + candidates_to_add + [p]):
                candidates_to_add.append(p)
                if len(current_stabilizers) + len(candidates_to_add) == num_qubits:
                    break

final_stabilizers = current_stabilizers + candidates_to_add
print(f"Total stabilizers: {len(final_stabilizers)}")

# Now construct the tableau
# Stim's Tableau.from_stabilizers expects stabilizers that generate a valid state.
# It returns a Tableau T such that T|0> is the state.
# Actually Tableau.from_stabilizers(stabilizers) -> Tableau
# Returns a tableau T such that T stabilizes the given stabilizers.
# Wait, let me check the docs or behavior.
# `stim.Tableau.from_stabilizers` takes a list of PauliStrings.
# It returns a tableau T such that T * Z_k * T^-1 = stabilizer[k].
# So T maps Z basis to the stabilizer basis.
# So applying T to |0> (which is stabilized by Z_k) gives the target state.

full_stabilizers = final_stabilizers
try:
    # Try with allow_underconstrained=True
    tableau = stim.Tableau.from_stabilizers(full_stabilizers, allow_underconstrained=True)
    circuit = tableau.to_circuit()
    print("Circuit generated.")
    
    # Verify
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check if stabilizers are satisfied
    satisfied = True
    for s in stabilizers_str:
        p = stim.PauliString(s)
        if not sim.measure_observable(p) == 0: # 0 means +1 eigenstate
            # Wait, measure_observable returns the measurement result.
            # If the state is a +1 eigenstate, it should always be False (0).
            # If -1, True (1).
            # But measure_observable collapses the state? No, peek_observable?
            # measure_observable(observable) -> bool
            # "Returns the result of measuring the observable. This is a non-destructive measurement if the state is already an eigenstate."
            # So if it returns True (1), it means -1 eigenvalue.
            # But wait, if it's not an eigenstate, it will project it.
            # Since we constructed the circuit from stabilizers, it SHOULD be an eigenstate.
            print(f"Stabilizer {s} not satisfied!")
            satisfied = False
            break
            
    if satisfied:
        print("Verification successful!")
        with open("data/gemini-3-pro-preview/agent_files/circuit_v1.stim", "w") as f:
            f.write(str(circuit))
    else:
        print("Verification failed.")

except Exception as e:
    print(f"Error generating tableau: {e}")

