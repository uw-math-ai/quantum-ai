import stim

def check():
    # Load circuit
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_solution_152.stim') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    # Load target stabilizers
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\target_stabilizers_152.txt') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    tableau = stim.Tableau.from_circuit(circuit)
    inverse_tableau = tableau.inverse()
    print(f"Tableau qubits: {len(tableau)}")
    
    stabilizers = [stim.PauliString(s) for s in stabilizers]
    print(f"Stabilizer length: {len(stabilizers[0])}")
    
    all_good = True
    for i, s in enumerate(stabilizers):
        conjugated = inverse_tableau(s)
        
        # Check if conjugated consists only of Z and I and has positive sign
        # We can check by seeing if it commutes with all X_i? No.
        # Stabilizers of |0> are +Z_i.
        # So the conjugated operator must be a product of Z_i with +1 phase.
        # This means no X or Y terms, and sign must be +1.
        
        # Check sign
        if conjugated.sign != 1:
            print(f"Stabilizer {i} failed: Sign is {conjugated.sign}")
            all_good = False
            continue
            
        # Check for non-Z components
        # We can convert to numpy or string to check.
        # String representation like "+Z_Z_"
        s_out = str(conjugated)
        if 'X' in s_out or 'Y' in s_out:
            print(f"Stabilizer {i} failed: contains X or Y: {s_out}")
            all_good = False
            continue
            
    if all_good:
        print("All stabilizers are preserved!")
    else:
        print("Some stabilizers failed.")

if __name__ == "__main__":
    check()
