import stim
import sys

def verify_circuit(circuit_str, stabilizers):
    try:
        circuit = stim.Circuit(circuit_str)
        # Tableau simulation
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        # Check stabilizers
        results = {}
        preserved = 0
        total = len(stabilizers)
        
        for i, s_str in enumerate(stabilizers):
            s = stim.PauliString(s_str)
            # Check if expectation value is +1
            # We can measure the stabilizer. If it's +1 deterministically, it's preserved.
            # But measuring collapses the state if it's not an eigenstate.
            # Better: peek_observable_expectation
            
            # Since we want to check if the state is stabilized by s, 
            # we check if s applied to state is state.
            # Or expectation value is +1.
            
            # Using peek_observable_expectation
            # result = sim.peek_observable_expectation(s) # Returns +1, -1, or 0 (indeterminate)
            
            # Actually peek_observable_expectation checks if the current state is an eigenstate.
            val = sim.peek_observable_expectation(s)
            if val == 1:
                results[s_str] = True
                preserved += 1
            else:
                results[s_str] = False
                
        print(f"Preserved: {preserved}/{total}")
        return preserved == total
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    with open("data/gemini-3-pro-preview/agent_files/circuit_171.stim", "r") as f:
        circuit_str = f.read()
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_171.txt", "r") as f:
        stabilizers = [l.strip() for l in f if l.strip()]
        
    verify_circuit(circuit_str, stabilizers)
