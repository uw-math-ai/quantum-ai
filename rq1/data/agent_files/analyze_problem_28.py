import stim
import numpy as np

stabilizers = [
    "XXXXIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXXIII",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIXXXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXXXXI",
    "ZZZZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZZIII",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIZZZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZZZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZZZI",
    "IXXIXIIIXXIXIIIXXIXIIIXXIXII",
    "IZZIZIIIZZIZIIIZZIZIIIZZIZII"
]

num_qubits = 28

# Verify number of qubits
print(f"Checking stabilizer lengths (expected {num_qubits})...")
for i, s in enumerate(stabilizers):
    if len(s) != num_qubits:
        print(f"Error: Stabilizer {i} has length {len(s)}")
    else:
        # print(f"Stabilizer {i}: {s}")
        pass

print(f"Number of stabilizers: {len(stabilizers)}")

# Check commutation
def commutes(p1, p2):
    # anti-commute if odd number of positions have different non-identity Paulis
    # X and Z anti-commute. Y is XZ.
    anti_commutations = 0
    for c1, c2 in zip(p1, p2):
        if c1 == 'I' or c2 == 'I':
            continue
        if c1 != c2:
            anti_commutations += 1
    return (anti_commutations % 2) == 0

print("Checking commutation...")
all_commute = True
for i in range(len(stabilizers)):
    for j in range(i + 1, len(stabilizers)):
        if not commutes(stabilizers[i], stabilizers[j]):
            print(f"Stabilizers {i} and {j} anti-commute!")
            print(f"{i}: {stabilizers[i]}")
            print(f"{j}: {stabilizers[j]}")
            all_commute = False

if all_commute:
    print("All stabilizers commute.")
else:
    print("Some stabilizers anti-commute.")

# Try to create a Tableau to see if it's a valid state (full rank)
try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    print("Tableau created successfully.")
    print(f"Tableau length: {len(tableau)}")
    # If len(stabilizers) < num_qubits, we might need to complete it or it's just underconstrained.
    # The prompt asks for a state defined by these generators. If it's underconstrained, any state in the subspace works?
    # Usually "the stabilizer state defined by these generators" implies they generate the full stabilizer group (maximal).
    # If 26 generators for 28 qubits, we are missing 2 generators? Or maybe dependent?
    
    # Find 2 additional stabilizers to fully constrain the state
    print("Finding additional stabilizers...")
    additional_stabilizers = []
    
    # Try simple Z operators
    for i in range(num_qubits):
        candidate = ['I'] * num_qubits
        candidate[i] = 'Z'
        candidate_str = "".join(candidate)
        
        # Check commutation
        commutes_all = True
        for s in stabilizers + additional_stabilizers:
            if not commutes(candidate_str, s):
                commutes_all = False
                break
        
        if commutes_all:
            # Check independence
            temp_stabilizers = stabilizers + additional_stabilizers + [candidate_str]
            mat = symplectic_matrix(temp_stabilizers)
            if rank_gf2(mat.copy()) == len(temp_stabilizers):
                print(f"Found additional stabilizer: {candidate_str}")
                additional_stabilizers.append(candidate_str)
                if len(stabilizers) + len(additional_stabilizers) == num_qubits:
                    break
    
    # Try simple X operators if needed
    if len(stabilizers) + len(additional_stabilizers) < num_qubits:
        for i in range(num_qubits):
            candidate = ['I'] * num_qubits
            candidate[i] = 'X'
            candidate_str = "".join(candidate)
            
            # Check commutation
            commutes_all = True
            for s in stabilizers + additional_stabilizers:
                if not commutes(candidate_str, s):
                    commutes_all = False
                    break
            
            if commutes_all:
                # Check independence
                temp_stabilizers = stabilizers + additional_stabilizers + [candidate_str]
                mat = symplectic_matrix(temp_stabilizers)
                if rank_gf2(mat.copy()) == len(temp_stabilizers):
                    print(f"Found additional stabilizer: {candidate_str}")
                    additional_stabilizers.append(candidate_str)
                    if len(stabilizers) + len(additional_stabilizers) == num_qubits:
                        break

    full_stabilizers = stabilizers + additional_stabilizers
    print(f"Total stabilizers: {len(full_stabilizers)}")
    
    # Generate circuit using Gaussian elimination
    # We can try to use stim.Tableau to generate a circuit?
    # No, stim doesn't have a direct 'tableau_to_circuit' method that's exposed easily for state prep.
    # But we can implement the standard algorithm:
    # 1. Start with target tableau.
    # 2. Apply Cliffords to reduce it to |0...0> state (Z basis).
    # 3. The inverse of the sequence prepares the state.
    
    # Or simply use the graph state approach.
    pass

except Exception as e:
    print(f"Error creating tableau: {e}")

