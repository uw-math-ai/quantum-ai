import stim
import sys

def test_stim_behavior():
    print(f"Stim version: {stim.__version__}")
    
    # Simple case: stabilizer X
    stabilizers = ["X"]
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
    circuit = tableau.to_circuit()
    print(f"Circuit for X: {circuit}")
    
    # Simulation
    sim = stim.TableauSimulator()
    sim.do(circuit)
    exp = sim.peek_observable_expectation(stim.PauliString("X"))
    print(f"Expectation of X: {exp}")
    
    if exp != 1:
        print("FAILURE: Expectation is not 1")
    else:
        print("SUCCESS: Expectation is 1")

if __name__ == "__main__":
    test_stim_behavior()
