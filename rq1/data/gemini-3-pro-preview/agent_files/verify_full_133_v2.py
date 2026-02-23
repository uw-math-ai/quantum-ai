import stim
import sys

def verify_full():
    print("Loading stabilizers...")
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print("Loading circuit...")
    with open("data/gemini-3-pro-preview/agent_files/circuit_133_cleaned.stim", "r") as f:
        circuit_text = f.read()

    print("Parsing circuit...")
    c = stim.Circuit(circuit_text)
    
    print("Simulating...")
    sim = stim.TableauSimulator()
    sim.do(c)
    
    # Get current inverse tableau T^-1 such that T^-1 |psi> = |0>
    # So T^-1 * S * T = Z_product
    # Or rather, for stabilizer S, we want U^dag S U to be a Z-product stabilizer of |0>.
    # sim.current_inverse_tableau() returns T such that T * State_current = |0>.
    # So T acts as U_dag.
    
    t_inv = sim.current_inverse_tableau()
    
    all_good = True
    for i, s_str in enumerate(stabilizers):
        p = stim.PauliString(s_str)
        
        # Apply T_inv to p
        # t_inv(p) returns the conjugated Pauli string U_dag P U.
        # However, stim.Tableau is not callable on PauliString directly in older versions?
        # In newer versions, we can use t_inv(p).
        # If not, use t_inv.call(p) or similar?
        # Let's try `t_inv(p)` first.
        
        try:
             # In stim, tableau(pauli_string) applies the tableau operation to the pauli string.
             # This computes T * P * T^-1.
             # Wait, tableau represents the Clifford operation C.
             # C(P) = C P C^-1.
             # We want U_dag P U.
             # Since t_inv represents U_dag, we want t_inv(P).
             p_prime = t_inv(p)
        except TypeError:
             print("Tableau not callable on PauliString? Trying other method.")
             # Check if we can use x_output, z_output?
             # No, easier: use simulator peeking.
             all_good = False
             break

        s_prime_str = str(p_prime)
        
        # Check if purely Z or I, and + sign
        # But wait, the string might be "X_Z__" for X on qubit 0? No, indices are implicit.
        # "+Z_Z__"
        
        if "X" in s_prime_str or "Y" in s_prime_str:
            print(f"Stabilizer {i} failed: Contains X/Y components. {s_prime_str}")
            all_good = False
            continue
            
        if "-" in s_prime_str: 
            # Note: str(p) usually puts sign at start "+XZ..." or "-XZ..."
            if s_prime_str.startswith("-"):
                 print(f"Stabilizer {i} failed: Sign is negative. {s_prime_str}")
                 all_good = False
                 continue
            
    if all_good:
        print("ALL STABILIZERS VERIFIED LOCALLY!")
    else:
        print("Verification failed.")

if __name__ == "__main__":
    verify_full()
