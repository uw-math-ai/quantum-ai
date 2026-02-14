import stim
import numpy as np

def solve_circuit():
    with open('stabilizers_36.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    # Convert to stim tableau
    # We have 34 stabilizers for 36 qubits?
    # Let's check how many there are.
    
    stabs = lines
    num_qubits = len(stabs[0])
    num_stabs = len(stabs)
    
    print(f"Num qubits: {num_qubits}")
    print(f"Num stabs: {num_stabs}")
    
    # We need to find a state that satisfies these stabilizers.
    # We can use stim.Tableau.from_stabilizers if we have N independent stabilizers for N qubits.
    # If we have fewer, we can pad with Z operators on the remaining degrees of freedom, or use a method that handles underconstrained systems.
    # But wait, stim.Tableau.from_stabilizers expects a full set of N stabilizers for N qubits to define a unique state.
    # If we have 34 stabilizers for 36 qubits, we have 2 logical qubits (or just unconstrained degrees of freedom).
    # We can just pick arbitrary stabilizers for the remaining 2 to fix a state.
    # Or we can check if they are independent first.
    
    # Let's try to create a tableau from these stabilizers, filling in the rest.
    
    pauli_stabs = [stim.PauliString(s) for s in stabs]
    
    # We can try to assume the other stabilizers are Z on the unconstrained qubits, 
    # but we need to know which ones they are.
    # A better way is to use Gaussian elimination to find the generators of the stabilizer group
    # and then complete the basis.
    
    # However, Stim's `Tableau.from_stabilizers` is quite strict.
    # It requires len(stabilizers) == num_qubits.
    # Let's try to add dummy stabilizers to make it full rank.
    
    # First, let's just see if we can find a state that satisfies these.
    # We can start with a tableau of size 36 (all |0>), and then project into the stabilizers?
    # No, that's measurement.
    
    # If we use `stim.Tableau.from_stabilizers`, we need to provide exactly 36 stabilizers.
    # We have 34.
    # Let's find 2 more stabilizers that commute with all existing ones and are independent.
    # Actually, let's just use the `solve_circuit_36_completion.py` strategy if I recall correctly (or write a new one).
    
    # Strategy:
    # 1. Use the given stabilizers.
    # 2. Find a set of commuting stabilizers that generates the group.
    # 3. Extend to a full set of 36 stabilizers.
    # 4. Use `stim.Tableau.from_stabilizers`.
    # 5. Convert to circuit.
    
    # To implement 2 & 3, we can use a small script with stim or symplectic algebra.
    # Since I don't want to implement full symplectic algebra if I can avoid it,
    # let's see if Stim can help.
    
    # Stim doesn't have a direct "complete this stabilizer set" function exposed easily in the python API 
    # (except implicitly via Tableau logic which might fail if underconstrained).
    # But `stim.Tableau.from_stabilizers(..., allow_underconstrained=True)` exists in recent versions!
    # Let's check if we can use that.
    
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
        print("Successfully created tableau from underconstrained stabilizers.")
    except Exception as e:
        print(f"Failed to create tableau directly: {e}")
        # If that fails, we might need to pad it manually.
        return

    # Once we have the tableau, we can convert to circuit.
    # 'elimination' method usually produces a circuit that prepares the state from |0>.
    circuit = tableau.to_circuit("elimination")
    
    # The circuit might be for the full tableau including the arbitrary choices made by `allow_underconstrained`.
    # But since the user only cares about the provided stabilizers, any state in the subspace is fine.
    # So this should work.
    
    print(circuit)

if __name__ == "__main__":
    solve_circuit()
