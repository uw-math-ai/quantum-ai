import stim
import sys

def analyze():
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim", "r") as f:
            circuit_str = f.read()
        
        circuit = stim.Circuit(circuit_str)
        num_qubits = circuit.num_qubits
        print(f"Circuit num_qubits: {num_qubits}")
        
        stab_len = len(stabilizers[0])
        print(f"Stabilizer length: {stab_len}")
        print(f"Number of stabilizers: {len(stabilizers)}")
        
        # Check if circuit prepares the stabilizers
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        preserved = 0
        for s_str in stabilizers:
            # Create a PauliString from the stabilizer string.
            # We assume the stabilizer string targets qubits 0, 1, ..., N-1.
            # If the circuit has M > N qubits, the extra qubits are ancillas.
            # We need to map the Pauli string to the correct qubits.
            
            # Since the stabilizer string is length N, and we assume data qubits are 0..N-1,
            # we can just use stim.PauliString(s_str).
            
            try:
                p = stim.PauliString(s_str)
            except Exception as e:
                print(f"Error parsing stabilizer: {s_str[:20]}... {e}")
                continue
                
            # Check expectation
            # peek_observable_expectation returns +1, -1, or 0.
            # If the state is stabilized by P, it should be +1.
            exp = sim.peek_observable_expectation(p)
            if exp == 1:
                preserved += 1
            
        print(f"Preserved stabilizers: {preserved} / {len(stabilizers)}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze()
