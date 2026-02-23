import stim
import sys

def check_locally(circuit_file, stabilizers_file):
    with open(circuit_file, 'r') as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    with open(stabilizers_file, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f.readlines() if line.strip()]
    
    stabilizers = []
    for s in lines:
        if len(s) < 171: s += 'I' * (171 - len(s))
        elif len(s) > 171: s = s[:171]
        stabilizers.append(stim.PauliString(s))
        
    print(f"Checking {len(stabilizers)} stabilizers...")
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    failures = []
    
    for i, s in enumerate(stabilizers):
        exp = sim.peek_observable_expectation(s)
        if exp != 1:
            failures.append((i, exp))
            
    if not failures:
        print("All stabilizers passed!")
    else:
        print(f"Failed stabilizers: {len(failures)}")
        for i, exp in failures[:10]:
            print(f"Stab {i}: Expectation {exp}")
            
    # Also check if failures are due to -1 (sign error) or 0 (not stabilized)
    sign_errors = [i for i, exp in failures if exp == -1]
    random_errors = [i for i, exp in failures if exp == 0]
    
    print(f"Sign errors (-1): {len(sign_errors)}")
    print(f"Not stabilized (0): {len(random_errors)}")
    
    return sign_errors

if __name__ == "__main__":
    circuit_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_171_corrected.stim"
    stabilizers_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_171.txt"
    check_locally(circuit_file, stabilizers_file)
