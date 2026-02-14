import stim
import sys

def solve():
    with open("target_stabilizers_72.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    stabilizers = []
    for line in lines:
        if ". " in line[:5]:
            line = line.split(". ", 1)[1]
        stabilizers.append(stim.PauliString(line))

    # We have 66 stabilizers. We need 72.
    # We can try to add Z_i or X_i on some qubits until we have 72 independent commuting stabilizers.
    
    # Let's try to add single qubit Z's as extra stabilizers.
    # We iterate through all qubits and try to add Z_i.
    
    n = 72
    current_stabs = list(stabilizers)
    
    # We need to check independence.
    # Let's build a tableau from the current stabilizers + extras.
    # Since we can't easily check independence with just PauliString list without Gaussian elimination,
    # let's try to use stim.Tableau.from_stabilizers iteratively?
    # No, that's expensive/not supported directly for partial.
    
    # Alternative: Use Gaussian elimination over GF(2).
    # Construct the check matrix.
    
    # But wait, if I just want *a* state, I can start with |0...0> and project into the stabilizer space?
    # No, measuring stabilizers is hard if they are high weight.
    
    # Let's try to complete the set.
    # We can use the tableau algorithm to find a completion.
    
    # Actually, stim.Tableau.from_stabilizers DOES support allowing underconstrained systems if we use `allow_underconstrained=True`?
    # Let's check if that arg exists.
    
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        print("Success with allow_underconstrained=True")
        
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated.")
        with open("solution_72.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"allow_underconstrained failed: {e}")
        # Try without allow_underconstrained if the argument is not supported
        try:
             tableau = stim.Tableau.from_stabilizers(stabilizers)
             circuit = tableau.to_circuit("elimination")
             with open("solution_72.stim", "w") as f:
                 f.write(str(circuit))
        except Exception as e2:
             print(f"Standard call failed: {e2}")
            
if __name__ == "__main__":
    solve()
