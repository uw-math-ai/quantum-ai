import stim
import sys
import os

def solve():
    # Read stabilizers
    stabs_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    with open(stabs_path, 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Check string length
    if not stabilizers:
        print("No stabilizers found.")
        return

    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}")

    # Convert to stim.PauliString
    pauli_stabs = []
    for i, s in enumerate(stabilizers):
        try:
            pauli_stabs.append(stim.PauliString(s))
        except Exception as e:
            print(f"Error parsing stabilizer {i}: {s}")
            raise e

    # Check commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(pauli_stabs)):
        for j in range(i + 1, len(pauli_stabs)):
            if not pauli_stabs[i].commutes(pauli_stabs[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
        # Print a few examples
        for k in range(min(5, len(anticommuting_pairs))):
            idx1, idx2 = anticommuting_pairs[k]
            print(f"  {idx1} and {idx2}")
        return 
    else:
        print("All stabilizers commute.")

    try:
        # Create a tableau from the stabilizers
        # allow_underconstrained=True is important if the stabilizers don't fully specify the state (less than 2^N stabilizers for N qubits)
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True, allow_redundant=True)
        
        # Convert to circuit
        # method="elimination" uses Gaussian elimination to find a circuit
        circuit = tableau.to_circuit("elimination")
        print("Successfully generated circuit.")
        
        # Verify the circuit
        print("Verifying circuit...")
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        failed_count = 0
        for i, s in enumerate(pauli_stabs):
            expectation = sim.peek_observable_expectation(s)
            if expectation != 1:
                # print(f"Stabilizer {i} failed: expectation {expectation}")
                failed_count += 1
        
        if failed_count == 0:
            print("Circuit verified successfully!")
            out_path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit.stim'
            with open(out_path, 'w') as f:
                f.write(str(circuit))
            print(f"Circuit written to {out_path}")
        else:
            print(f"Circuit verification failed. {failed_count} stabilizers failed.")

    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
