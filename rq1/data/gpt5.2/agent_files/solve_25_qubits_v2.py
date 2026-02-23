import stim
import sys

# Define the stabilizers
stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIIIIIIZXIXZ",
    "XXXXXZZZZZZZZZZXXXXXIIIII",
    "IIIIIXXXXXZZZZZZZZZZXXXXX",
    "XXXXXIIIIIXXXXXZZZZZZZZZZ",
    "ZZZZZXXXXXIIIIIXXXXXZZZZZ"
]

def check_commutativity(stabs):
    n = len(stabs)
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            s1 = stabs[i]
            s2 = stabs[j]
            commutation_count = 0
            for k in range(len(s1)):
                p1 = s1[k]
                p2 = s2[k]
                if p1 != 'I' and p2 != 'I' and p1 != p2:
                    commutation_count += 1
            if commutation_count % 2 == 1:
                anticommuting_pairs.append((i, j))
    return anticommuting_pairs

print("Checking commutativity...")
anticomms = check_commutativity(stabilizers)
if anticomms:
    print(f"Found {len(anticomms)} anticommuting pairs!")
    for i, j in anticomms:
        print(f"  {i} vs {j}")
        # print(f"  {stabilizers[i]}")
        # print(f"  {stabilizers[j]}")
else:
    print("All stabilizers commute.")

print("\nAttempting to generate circuit with Stim...")
try:
    pauli_stabs = [stim.PauliString(s) for s in stabilizers]
    # Allow underconstrained because we have 24 stabilizers for 25 qubits
    tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    print("Successfully generated circuit!")
    # print(circuit)
    
    # Save circuit to file
    with open("circuit_25_qubits.stim", "w") as f:
        f.write(str(circuit))
        
except Exception as e:
    print(f"Error: {e}")
