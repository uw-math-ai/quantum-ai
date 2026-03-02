import stim
import numpy as np

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def solve():
    filename = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_175.txt"
    stabilizers = parse_stabilizers(filename)
    num_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)
    
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {num_stabilizers}")

    # Create a Tableau from the stabilizers.
    # If the number of stabilizers equals the number of qubits, we can try to form a Tableau directly.
    # If not, we need to complete the basis or use a different method.
    
    stabilizers_obj = [stim.PauliString(s) for s in stabilizers]
    
    # Check independence and commutativity
    # ...
    
    try:
        # Pad with a dummy stabilizer if needed to make it 175
        if num_stabilizers < num_qubits:
             print(f"Padding {num_qubits - num_stabilizers} stabilizers.")
             # We need to find a Pauli string that commutes with all and is independent.
             # Alternatively, we can just use the provided ones and let stim handle it?
             # stim.Tableau.from_stabilizers might not support underconstrained well in this version?
             # Let's try to just use the 174 and see if it works.
             pass

        t = stim.Tableau.from_stabilizers(stabilizers_obj, allow_underconstrained=True, allow_redundant=True)
        print("Successfully created Tableau from stabilizers (with redundant/underconstrained allowed).")
        
        # Now convert to circuit
        # The circuit will map Z basis states to the stabilizer states.
        # But we want to map |0...0> to the state.
        # The tableau T maps Z_k to stabilizer_k.
        # So U |0...0> = |psi> where Z_k |0...0> = |0...0> and U Z_k U^dag = stabilizer_k.
        # This is exactly what T.to_circuit() provides (inverse operation).
        
        c = t.to_circuit()
        
        # Verify the circuit against the provided stabilizers
        sim = stim.TableauSimulator()
        sim.do_circuit(c)
        
        all_good = True
        for i, s in enumerate(stabilizers_obj):
            expectation = sim.peek_observable_expectation(s)
            if expectation != 1:
                print(f"Stabilizer {i} not satisfied. Expectation: {expectation}")
                all_good = False
                break
        
        if all_good:
            print("All provided stabilizers are satisfied by the generated circuit.")
            
            # Save the circuit to a file
            circuit_str = str(c)
            with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_175.stim", "w") as f:
                f.write(circuit_str)
            print("Circuit written to circuit_175.stim")
        else:
            print("Circuit verification failed.")

    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    solve()
