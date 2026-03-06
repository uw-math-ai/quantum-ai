import stim

def solve():
    try:
        # Read stabilizers
        with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Read {len(lines)} stabilizers.")

        pauli_strings = []
        for line in lines:
            p = stim.PauliString(line)
            pauli_strings.append(p)
        
        print(f"First pauli string length: {len(pauli_strings[0])}")

        # Create tableau
        # We need allow_underconstrained=True because we have 68 stabilizers for 75 qubits.
        # allow_redundant=True just in case.
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_underconstrained=True, allow_redundant=True)
        
        print(f"Tableau has {len(tableau)} qubits")
        
        for i, p in enumerate(pauli_strings):
            if len(p) != 75:
                print(f"Pauli string {i} has length {len(p)}")
        
        # Generate circuit
        # method="elimination" works well for stabilizer states.
        circuit = tableau.to_circuit("elimination")
        
        print(f"Circuit has {circuit.num_qubits} qubits")
        
        # Verify the circuit
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Check if the state prepared by the circuit satisfies all stabilizers
        all_good = True
        for i, p in enumerate(pauli_strings):
            # peek_observable_expectation returns +1 or -1 (or 0 if random)
            expectation = sim.peek_observable_expectation(p)
            if expectation != 1:
                print(f"Failed stabilizer {i}: {lines[i]} (expectation {expectation})")
                all_good = False
        
        if all_good:
            print("Circuit generated successfully and verified locally.")
            output_path = "data/gemini-3-pro-preview/agent_files/circuit_75.stim"
            with open(output_path, "w") as f:
                f.write(str(circuit))
            print(f"Circuit written to {output_path}")
        else:
            print("Circuit generation failed verification.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
