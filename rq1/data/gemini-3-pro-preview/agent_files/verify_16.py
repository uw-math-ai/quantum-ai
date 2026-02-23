import stim

def verify():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_85_v2.stim', 'r') as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    s = stim.PauliString("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI")
    
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    print(f"Expectation: {sim.peek_observable_expectation(s)}")
    
    # Measure
    res = sim.measure_observable(s)
    print(f"Measured: {res}")
    
if __name__ == "__main__":
    verify()
