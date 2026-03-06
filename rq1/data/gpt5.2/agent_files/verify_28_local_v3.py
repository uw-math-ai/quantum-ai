import stim
import sys

def verify_circuit(circuit_str, stabilizers_file):
    with open(stabilizers_file, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    try:
        circuit = stim.Circuit(circuit_str)
    except Exception as e:
        print(f"Error parsing circuit: {e}")
        return

    # Simulate the circuit
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    # Check each stabilizer
    all_good = True
    for i, stab in enumerate(stabilizers):
        expectation = sim.peek_observable_expectation(stab)
        if expectation != 1:
            print(f"Stabilizer {i} failed: {stab} -> {expectation}")
            all_good = False
            
    if all_good:
        print("All stabilizers passed locally!")
    else:
        print("Some stabilizers failed.")

circuit_str = """
H 0 8
CX 0 8 0 12 0 16 0 25
H 4 24
CX 4 0 24 0 12 1 1 12 12 1 1 25 24 1 25 2 2 25 25 2 2 16 4 2 13 2 17 2 18 2 19 2 21 2 22 2 23 2 24 2 26 2 27 2 20 3 3 20 20 3 8 3 13 3 16 3 17 3 18 3 19 3 21 3 22 3 23 3 26 3 27 3 4 16 8 4 8 5 5 8 8 5 5 16 16 6 6 16 16 6 13 6 17 6 18 6 19 6 21 6 22 6 23 6 26 6 27 6 8 7 7 8 8 7
H 7 12 20 25
CX 7 12 7 13 7 17 7 20 7 24 7 25 7 26 7 27 12 7 24 7 24 8 8 24 24 8 8 17 8 20 8 25 8 26 8 27 12 8 17 9 9 17 17 9 13 9 21 9 17 10 10 17 17 10
H 10
CX 10 12 10 21 12 11 11 12 12 11 11 13 11 21 13 12 12 13 13 12 12 21 21 13 13 21 21 13 16 14 14 16 16 14
H 14
CX 14 16 14 18 25 14 25 15 15 25 25 15 15 18 15 27 18 16 16 18 18 16 22 16 27 16
H 17
CX 17 22 17 27 18 22 27 18 27 19 19 27 27 19 22 20 20 22 22 20 24 21 21 24 24 21
H 21
CX 21 25 21 27 22 21 22 26 22 27 27 23 23 27 27 23 26 23 27 23
H 24
CX 24 26 24 27 25 27 26 25
"""

verify_circuit(circuit_str, "stabilizers_28.txt")
