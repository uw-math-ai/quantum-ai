import stim
import sys

def check():
    try:
        # Read stabilizers
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_120.txt', 'r') as f:
            stabilizers = [l.strip() for l in f if l.strip()]
        
        # Read circuit
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_120.stim', 'r') as f:
            circuit_text = f.read()
        
        circuit = stim.Circuit(circuit_text)
        
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        failed = []
        for i, s_str in enumerate(stabilizers):
            s = stim.PauliString(s_str)
            expectation = sim.peek_observable_expectation(s)
            if expectation != 1:
                print(f"Failed stabilizer {i}: {s_str} (expectation {expectation})")
                failed.append(s_str)
        
        if not failed:
            print("All stabilizers passed locally.")
        else:
            print(f"Failed {len(failed)} stabilizers locally.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
