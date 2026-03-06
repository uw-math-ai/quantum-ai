import stim
import sys

def verify():
    # Load stabilizers
    path_stabs = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_153.txt'
    with open(path_stabs, 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    # Load circuit
    path_circ = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_153_v2.stim'
    with open(path_circ, 'r') as f:
        circuit_text = f.read()
        
    circuit = stim.Circuit(circuit_text)
    
    # Calculate the tableau of the circuit
    # The circuit maps |0> to the state.
    # We want to check if the stabilizers stabilize this state.
    # state = U |0>
    # Stabilizer S stabilizes state if S |psi> = |psi>
    # <=> S U |0> = U |0>
    # <=> U^dag S U |0> = |0>
    # So we conjugate the stabilizers by the inverse of the circuit, and check if the result is in the stabilizer group of |0> (i.e. consists of Zs on qubits that are 0).
    # Alternatively, we can just evolve |0> by the circuit and check the stabilizers.
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    print(f"Checking {len(stabilizers)} stabilizers...")
    passed = 0
    for i, s_str in enumerate(stabilizers):
        # The stabilizer string might need to be padded or truncated if the circuit uses more qubits.
        # The circuit uses up to 154 (so 155 qubits).
        # The stabilizer is defined on 0..152.
        # We can pad the stabilizer with I's.
        
        # Parse PauliString
        p = stim.PauliString(s_str)
        
        # Check if expectation value is +1
        # peek_observable_expectation returns 1 or -1 or 0 (if random).
        # We want +1.
        exp = sim.peek_observable_expectation(p)
        
        if exp == 1:
            passed += 1
        else:
            print(f"Stabilizer {i} failed: {s_str} -> expectation {exp}")
            
    print(f"Passed {passed}/{len(stabilizers)}")

if __name__ == "__main__":
    verify()
