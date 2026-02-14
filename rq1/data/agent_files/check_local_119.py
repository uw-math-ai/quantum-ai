import stim
import sys

def check():
    # Load stabilizers
    with open("target_stabilizers_119_v2.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    # Load circuit
    with open("circuit_119_v2.stim", "r") as f:
        circuit_text = f.read()
    
    try:
        circuit = stim.Circuit(circuit_text)
    except Exception as e:
        print(f"Circuit syntax error: {e}")
        return

    # The circuit should prepare the state from |0...0>
    # We can check if the stabilizers are stabilized by the output state.
    # The output state is C |0...0>
    # A stabilizer S stabilizes |psi> if S |psi> = |psi>
    # Equivalently, C^dag S C stabilizes |0...0>
    # Which means C^dag S C should be a product of Z operators on qubits initialized to 0.
    # Or simpler:
    # Use Tableau simulator.
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    all_good = True
    for i, s_str in enumerate(stabilizers):
        s = stim.PauliString(s_str)
        expectation = sim.peek_observable_expectation(s)
        if expectation != 1:
            print(f"Stabilizer {i} failed: {s_str}, expectation={expectation}")
            all_good = False
            # break # Don't break, see how many fail
    
    if all_good:
        print("All stabilizers preserved!")
    else:
        print("Some stabilizers failed.")

if __name__ == "__main__":
    check()
