import stim

def solve():
    filename = "stabilizers_175.txt"
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(s) for s in lines]
    
    # We have 174 stabilizers for 175 qubits.
    # We can try to use stim to complete it.
    try:
        # allow_underconstrained=True allows fewer stabilizers than qubits
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        # The tableau T satisfies T(Z_k) = stabilizers[k] for k < len(stabilizers)
        # And for the remaining qubits, it picks something compatible.
        # The circuit C = T.to_circuit() implements the unitary U such that U Z_k U^dag = S_k.
        # So U |0> is the +1 eigenstate of S_k.
        # This is exactly what we want.
        
        c = t.to_circuit()
        
        # Verify
        sim = stim.TableauSimulator()
        sim.do_circuit(c)
        
        failed = False
        for i, s in enumerate(stabilizers):
            if sim.peek_observable_expectation(s) != 1:
                print(f"Stabilizer {i} failed.")
                failed = True
                break
        
        if not failed:
            print("Circuit verified successfully.")
            with open("circuit_175.stim", "w") as f:
                f.write(str(c))
        else:
            print("Circuit verification failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
