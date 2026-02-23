import stim

def solve():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_42.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing stabilizer: {line}, {e}")
            return

    try:
        # Create a tableau from the stabilizers
        # allow_underconstrained=True is needed because we have 38 stabilizers for 42 qubits
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        # If from_stabilizers fails, it might be due to inconsistencies.
        # Let's check for inconsistencies if that happens, but first try this.
        return

    # Generate circuit
    circuit = tableau.to_circuit("elimination")
    
    # Verify the circuit
    # We can simulate the circuit and check if the output state is stabilized by the generators.
    # Since we have a Clifford circuit and stabilizer state, we can use the tableau simulator.
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    all_good = True
    for i, stab in enumerate(stabilizers):
        # measure_expectation returns +1, -1, or 0 (if random)
        expectation = sim.peek_observable_expectation(stab)
        if expectation != 1:
            print(f"Stabilizer {i} not satisfied: {stab}, expectation: {expectation}")
            all_good = False
            
    if all_good:
        print("Circuit verified locally!")
        print("---CIRCUIT START---")
        print(circuit)
        print("---CIRCUIT END---")
    else:
        print("Circuit failed verification.")

if __name__ == "__main__":
    solve()
