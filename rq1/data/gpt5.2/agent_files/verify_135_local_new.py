import stim

def verify_circuit_local():
    with open(r'data/gemini-3-pro-preview/agent_files/circuit_135_fixed.stim', 'r') as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    
    with open('data/gemini-3-pro-preview/agent_files/stabilizers_135.txt', 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    s44 = stabs[44]
    s59 = stabs[59]
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    e44 = sim.peek_observable_expectation(stim.PauliString(s44))
    e59 = sim.peek_observable_expectation(stim.PauliString(s59))
    
    print(f"Local verify 44: {e44}")
    print(f"Local verify 59: {e59}")

if __name__ == "__main__":
    verify_circuit_local()
