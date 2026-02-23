import stim

def check_sign():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    s54 = stim.PauliString(stabilizers[54])
    
    # Load circuit
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_133.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    # Measure s54 multiple times
    for i in range(10):
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        res = sim.measure_observable(s54)
        print(f"Expectation of stabilizer 54: {res}")

if __name__ == "__main__":
    check_sign()
