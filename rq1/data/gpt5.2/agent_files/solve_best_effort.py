import stim

stabilizers = [
    "XXIIIXXIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXIIIXXIIIIIIII",
    "IIIIIIXXIIIXXIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXIIIXXII",
    "IIXXIIIXXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIXXIIIXXIIIIII",
    "IIIIIIIIXXIIIXXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXIIIXX",
    "IIIIXIIIIXIIIIIIIIIIIIIII",
    "IIIIIXIIIIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIXIIIIXIIIII",
    "IIIIIIIIIIIIIIIXIIIIXIIII",
    "IIIIIZZIIIZZIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZIIIZZIII",
    "IZZIIIZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIZZIIIZZIIIIIII",
    "IIIIIIIZZIIIZZIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZIIIZZI",
    "IIIZZIIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIZZIIIZZIIIII",
    "ZZIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZII",
    "IIZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZZ"
]

# Try to find a maximal commuting set
# We prioritize Z stabilizers (since they are already satisfied by |0>) and then add X stabilizers that commute.
# Actually, the user probably wants the best effort.

def solve_best_effort():
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    # Greedy approach: keep adding stabilizers if they commute with everything so far
    # But maybe we should prioritize the ones that are hard?
    # Or just use Stim's tableau from stabilizers with allow_underconstrained=True on a filtered list?
    
    # Let's try to remove the minimal number of stabilizers to make it commuting.
    # We saw 2 pairs. 
    # Pair 1: 10 and 16.
    # Pair 2: 10 and 17.
    # If we remove 10, both conflicts are resolved.
    # Let's check if removing 10 leaves a commuting set.
    
    good_indices = [i for i in range(len(stabilizers)) if i != 10]
    good_paulis = [paulis[i] for i in good_indices]
    
    conflict = False
    for i in range(len(good_paulis)):
        for j in range(i+1, len(good_paulis)):
            if not good_paulis[i].commutes(good_paulis[j]):
                print(f"Still conflict between some stabilizers after removing 10")
                conflict = True
                break
        if conflict: break
    
    if not conflict:
        print("Removing index 10 resolves all conflicts.")
        try:
            tableau = stim.Tableau.from_stabilizers(good_paulis, allow_underconstrained=True)
            circuit = tableau.to_circuit("elimination")
            print("CIRCUIT_START")
            print(circuit)
            print("CIRCUIT_END")
            return
        except Exception as e:
            print(f"Error: {e}")

    # If removing 10 wasn't enough, we might need to remove more.
    # Let's try to just build a tableau from the largest commuting subset we can find.
    
    commuting_set = []
    for p in paulis:
        if all(p.commutes(existing) for existing in commuting_set):
            commuting_set.append(p)
    
    print(f"Found commuting set of size {len(commuting_set)}")
    try:
        tableau = stim.Tableau.from_stabilizers(commuting_set, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        print("CIRCUIT_START")
        print(circuit)
        print("CIRCUIT_END")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_best_effort()
