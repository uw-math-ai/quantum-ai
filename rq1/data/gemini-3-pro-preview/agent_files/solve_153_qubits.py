import stim
import sys

def solve():
    print("Reading stabilizers...")
    # Read stabilizers
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_153_current.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Read {len(lines)} stabilizers.")
    if not lines:
        print("Error: No stabilizers read.")
        return

    # Check length
    lengths = [len(l) for l in lines]
    if len(set(lengths)) > 1:
        print(f"Error: Stabilizers have different lengths: {set(lengths)}")
        return

    num_qubits = lengths[0]
    print(f"Number of qubits: {num_qubits}")

    # Convert to PauliStrings
    try:
        stabilizers = [stim.PauliString(s) for s in lines]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Check commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    
    # Check all pairs
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for idx, (i, j) in enumerate(anticommuting_pairs):
            if idx < 10:
                print(f"  {i} and {j} anticommute")
        if len(anticommuting_pairs) > 10:
            print("  ...")
    else:
        print("All stabilizers commute.")

    # Try to generate circuit
    try:
        print("Generating tableau from stabilizers...")
        # allow_underconstrained=True handles missing degrees of freedom
        # allow_redundant=True handles redundant stabilizers if consistent
        # But allow_redundant=True won't fix anticommutation
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        print("Successfully generated circuit.")
        
        # Verify internally
        print("Verifying circuit internally...")
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        satisfied_count = 0
        for i, stab in enumerate(stabilizers):
            if sim.measure_observable(stab) == False: # False means +1 eigenvalue result (measurement 0)
                 satisfied_count += 1
            else:
                 print(f"Internal check failed for stabilizer {i}")

        print(f"Satisfied {satisfied_count}/{len(stabilizers)} stabilizers.")
        
        if satisfied_count == len(stabilizers):
            print("Internal check passed!")
        else:
            print("Internal check failed.")
            
        with open(r'data/gemini-3-pro-preview/agent_files/circuit_153.stim', 'w') as f:
            f.write(str(circuit))

    except Exception as e:
        print(f"Error generating tableau: {e}")

if __name__ == "__main__":
    solve()
