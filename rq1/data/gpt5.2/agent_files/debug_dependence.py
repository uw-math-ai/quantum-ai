import stim
import sys

# Failing stabilizer is at index 15 (0-indexed)
failing_index = 15

# Read stabilizers
with open("stabilizers_54_v2.txt", "r") as f:
    stabilizers = [l.strip() for l in f if l.strip()]

stim_stabs = [stim.PauliString(s) for s in stabilizers]
print(f"Total stabilizers: {len(stim_stabs)}")

failing_stab = stim_stabs[failing_index]
print(f"Checking stabilizer {failing_index}: {failing_stab}")

# Create tableau from all others
others = stim_stabs[:failing_index] + stim_stabs[failing_index+1:]
try:
    # If this fails, then others are inconsistent among themselves
    t_others = stim.Tableau.from_stabilizers(others, allow_underconstrained=True)
    print("Tableau for 'others' created.")
    
    circuit = t_others.to_circuit("elimination")
    
    # Simulate to see what the failing stabilizer value is
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    # We can measure the failing stabilizer
    # But sim.measure returns random result if expectation is 0
    # Use peek_observable_expectation
    val = sim.peek_observable_expectation(failing_stab)
    print(f"Expectation of failing stabilizer: {val}")
    
    if val == 0:
        print("Result 0 means INDEPENDENT. The failing stabilizer adds a new constraint.")
    elif val == 1:
        print("Result 1 means DEPENDENT and CONSISTENT (+1).")
    elif val == -1:
        print("Result -1 means DEPENDENT and INCONSISTENT (-1). The other stabilizers imply -1.")
        
except Exception as e:
    print(f"Error creating tableau: {e}")
