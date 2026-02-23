import stim
import sys

generators = [
    "XXXXXXIII",
    "XXXIIIXXX",
    "ZZIIIIIII",
    "ZIZIIIIII",
    "IIIZZIIII",
    "IIIZIZIII",
    "IIIIIIZZI",
    "IIIIIIZIZ"
]

def check_commutativity(gens):
    print(f"Checking {len(gens)} generators...")
    for i in range(len(gens)):
        for j in range(i + 1, len(gens)):
            g1 = stim.PauliString(gens[i])
            g2 = stim.PauliString(gens[j])
            if not g1.commutes(g2):
                print(f"Anticommute: {i} ({gens[i]}) and {j} ({gens[j]})")
                return False
    print("All commute.")
    return True

if check_commutativity(generators):
    try:
        # Try to form a tableau. Since it's 8 gens for 9 qubits, we might need to complete it or use allow_underconstrained.
        t = stim.Tableau.from_stabilizers([stim.PauliString(g) for g in generators], allow_underconstrained=True)
        print("Tableau created successfully.")
        
        # We can create a circuit from the tableau
        # Since we have 8 stabilizers for 9 qubits, we effectively have 1 logical qubit.
        # The method to_circuit() might work if we treat it as a state (stabilizers + destablizers)
        # But here we only have stabilizers.
        # However, we can use the graph state approach or simply use the Tableau to generate a circuit.
        # stim.Tableau.from_stabilizers creates a tableau that stabilizes the given generators.
        # It fills in the rest with arbitrary stabilizers/destabilizers.
        # Then we can convert this full tableau to a circuit that prepares |0...0> -> StabilizerState.
        
        circ = t.to_circuit("elimination")
        print("Circuit generated.")
        print(circ)
        
    except Exception as e:
        print(f"Error creating tableau: {e}")
