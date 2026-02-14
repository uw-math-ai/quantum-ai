import stim

def solve():
    with open("target_stabilizers_124.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    # Convert to stim.PauliString
    pauli_stabs = [stim.PauliString(s) for s in stabs]
    
    # Check length
    num_qubits = len(stabs[0])
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {len(stabs)}")
    
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully")
        
        # Verify circuit
        # Simulating the circuit to check stabilizers
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        all_passed = True
        for i, s in enumerate(pauli_stabs):
            # check if expectation value is +1
            res = sim.measure_observable(s)
            if res != 0: # 0 means +1 eigenvalue, 1 means -1 eigenvalue
                print(f"Stabilizer {i} failed: {s}")
                all_passed = False
        
        if all_passed:
            print("All stabilizers passed verification locally.")
            with open("solve_stabilizers_124.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Verification failed.")
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
