
import stim

def verify():
    # Read stabilizers
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_161.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Read circuit
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_161.stim', 'r') as f:
        circuit_text = f.read()

    circuit = stim.Circuit(circuit_text)
    
    # We need to check if the circuit prepares a state stabilized by the stabilizers.
    # The circuit prepares a state |psi> = U|0>.
    # We need S |psi> = |psi> for all S in stabilizers.
    # Equivalently, U^dagger S U |0> = |0>.
    # So U^dagger S U must be a stabilizer of |0>, which means it must be purely Z-type (or I).
    # And the sign must be +1.
    
    tableau = stim.Tableau.from_circuit(circuit)
    
    preserved_count = 0
    total_count = len(stabilizers)
    
    print(f"Checking {total_count} stabilizers...")
    
    for i, s_str in enumerate(stabilizers):
        s = stim.PauliString(s_str)
        
        # We want to check if the state is stabilized by s.
        # One way is to peek at the expectation value using the tableau.
        # But tableau.peek_observables requires a collapsed state? No.
        
        # Let's map the stabilizer by the inverse tableau.
        # The tableau T represents the operation U.
        # We want to check if U |0> is stabilized by S.
        # This is equivalent to checking if |0> is stabilized by U^dagger S U.
        # U^dagger S U is the result of conjugating S by U^dagger.
        # T.inverse() represents U^dagger.
        
        inv_tableau = tableau.inverse()
        mapped_s = s.after(inv_tableau)
        
        # Check if mapped_s is +Z or +I on non-zero indices.
        # More precisely, mapped_s must stabilize |0>.
        # This means it must be a product of Z operators on various qubits, with +1 phase.
        # If it has any X or Y, it doesn't stabilize |0> (it flips it or phases it).
        # If it has - sign, it stabilizes |1> (or similar), not |0>.
        
        # Actually, let's be more precise.
        # A Pauli string P stabilizes |0> iff P only contains I and Z operators, and its sign is +1.
        
        is_preserved = True
        
        if mapped_s.sign != +1:
            is_preserved = False
        else:
            # Check for X or Y components
            # stim PauliString doesn't have a direct "has_x_or_y" method, but we can iterate or check logic.
            # Convert to numpy or string.
            # String representation might be easiest.
            ms_str = str(mapped_s)
            # ms_str starts with sign, e.g. "+Z_Z_"
            if 'X' in ms_str or 'Y' in ms_str:
                is_preserved = False
                
        if is_preserved:
            preserved_count += 1
        else:
            # print(f"Stabilizer {i} NOT preserved. Mapped to: {mapped_s}")
            pass
            
    print(f"Preserved: {preserved_count}/{total_count}")
    
    if preserved_count == total_count:
        print("SUCCESS: All stabilizers preserved.")
    else:
        print("FAILURE: Some stabilizers not preserved.")

if __name__ == "__main__":
    verify()
