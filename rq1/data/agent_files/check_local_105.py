import stim
import sys

def check_locally():
    try:
        with open('circuit_candidate_105.stim', 'r') as f:
            circuit = stim.Circuit(f.read())
            
        with open('my_stabilizers_105.txt', 'r') as f:
            stabilizers = [line.strip() for line in f if line.strip()]

        print(f"Checking {len(stabilizers)} stabilizers...")
        
        # Calculate the tableau of the circuit.
        # T * |0> = |psi>.
        # We want S |psi> = |psi> for all S.
        # This means S T |0> = T |0>.
        # T^-1 S T |0> = |0>.
        # So T^-1 S T must be in the stabilizer group of |0>, which is <Z_0, Z_1, ...>.
        # This means T^-1 S T must be a product of Z operators (and Identity) with +1 phase.
        
        tableau = stim.Tableau.from_circuit(circuit)
        inv_tableau = tableau.inverse()
        
        preserved = 0
        total = len(stabilizers)
        
        for i, s_str in enumerate(stabilizers):
            s = stim.PauliString(s_str)
            
            # transform s by T^-1
            transformed = inv_tableau(s)
            
            # Check if transformed is all Z or I and phase is +1.
            # sign: +1 -> 0, -1 -> 2 (in Z_4 representation used internally maybe?)
            # Stim docs say sign is +1 or -1.
            
            if transformed.sign != 1:
                # print(f"Stabilizer {i} failed phase: {transformed.sign}")
                continue
            
            is_valid = True
            # Check for X or Y components
            # We can use numpy conversion
            # 0=I, 1=X, 2=Y, 3=Z
            # We want only 0 and 3.
            
            # Or just check commutation with all Z_k? No.
            # Check if it commutes with all X_k? No.
            # Just check if it's diagonal.
            
            # Stim PauliString doesn't expose components easily in Python API without numpy?
            # Actually you can iterate it?
            # Or just use __str__ and check for X or Y?
            
            t_str = str(transformed)
            if 'X' in t_str or 'Y' in t_str:
                # print(f"Stabilizer {i} failed Pauli: {t_str}")
                is_valid = False
            
            if is_valid:
                preserved += 1

        print(f"Preserved: {preserved}/{total}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_locally()
