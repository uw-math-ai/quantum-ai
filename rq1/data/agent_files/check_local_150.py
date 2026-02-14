import stim
import sys

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def check():
    try:
        stabilizers = load_stabilizers('target_stabilizers_150.txt')
        with open('solve_150_circuit.stim', 'r') as f:
            circuit_text = f.read()
        
        circuit = stim.Circuit(circuit_text)
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        failed = []
        for i, s_str in enumerate(stabilizers):
            s = stim.PauliString(s_str)
            expectation = sim.peek_observable_expectation(s)
            
            # expectation is +1, -1, or 0 (uncertain)
            if expectation != 1:
                failed.append((i, s_str, expectation))
        
        if not failed:
            print("SUCCESS: All stabilizers preserved.")
        else:
            print(f"FAILURE: {len(failed)} stabilizers not preserved.")
            for i, s, exp in failed[:5]:
                print(f"  Stabilizer {i}: Expectation {exp}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
