import stim
import sys

def check():
    with open("stabilizers_68.txt", 'r') as f:
        stabilizers = [stim.PauliString(l.strip()) for l in f if l.strip()]
    
    with open("circuit_68.stim", 'r') as f:
        circuit = stim.Circuit(f.read())
        
    print(f"Circuit instructions: {len(circuit)}")
    
    # Check if the circuit preserves the stabilizers
    # Strategy:
    # The circuit prepares a state |psi> from |0>.
    # We want <psi| S |psi> = +1 for all S in stabilizers.
    # Equivalently, S |psi> = |psi>.
    # Equivalently, Udag S U |0> = |0>.
    # Where U is the circuit.
    # So we conjugate each S by Udag (inverse circuit) and check if it becomes a product of Zs on qubits that were initialized to 0.
    
    # Or, simpler in Stim:
    # Tableau simulator.
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check stabilizers
    all_passed = True
    for i, s in enumerate(stabilizers):
        # We can use peek_observable_expectation(s)
        # But that might be slow if we do it for all.
        # Actually for stabilizer states it returns +1, -1 or 0.
        exp = sim.peek_observable_expectation(s)
        if exp != 1:
            print(f"Stabilizer {i} failed: expectation {exp}")
            all_passed = False
            # break
            
    if all_passed:
        print("SUCCESS: All stabilizers preserved!")
    else:
        print("FAILURE: Some stabilizers not preserved.")

if __name__ == "__main__":
    check()
