import stim
import sys

def verify():
    # Read stabilizers
    with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_49_task.txt", "r") as f:
        # Convert strings to stim.PauliString
        stabilizers = [stim.PauliString(line.strip()) for line in f if line.strip()]

    try:
        # Read generated circuit
        with open("circuit_49_generated.stim", "r") as f:
            circuit_text = f.read()
            circuit = stim.Circuit(circuit_text)
    except Exception as e:
        print(f"Error reading circuit: {e}")
        return

    # To check if U |0> is stabilized by S, we check if U^dag S U |0> = |0>.
    # This means U^dag S U must be a product of Z_i and I operators with +1 phase.
    
    # We can compute U^dag S U directly using stim.Tableau.from_circuit(circuit).inverse()(S).
    # But wait, tableau inverse is U^dag.
    tableau_inv = stim.Tableau.from_circuit(circuit).inverse()

    all_good = True
    for i, s in enumerate(stabilizers):
        s_prime = tableau_inv(s)
        
        # Check if s_prime consists only of I and Z
        # Stim PauliString has method `commutes` but not `is_z_type` directly.
        # But we can check string representation.
        s_str = str(s_prime)
        
        # Check for X or Y
        has_x = "X" in s_str
        has_y = "Y" in s_str
        
        if has_x or has_y:
            print(f"Stabilizer {i} maps to non-Z string: {s_prime}")
            all_good = False
            continue
            
        # Check sign. Sign is 1, -1, 1j, -1j.
        if s_prime.sign != 1:
            print(f"Stabilizer {i} has wrong sign: {s_prime.sign}")
            all_good = False
            continue

    if all_good:
        print("All stabilizers preserved!")
    else:
        print("Some stabilizers failed.")

if __name__ == "__main__":
    verify()
