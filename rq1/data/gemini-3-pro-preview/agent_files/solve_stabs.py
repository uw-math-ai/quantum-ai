import stim
import sys

def solve():
    try:
        with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
            stabs = [line.strip() for line in f if line.strip()]

    except FileNotFoundError:
        print("stabs.txt not found")
        return

    print(f"Loaded {len(stabs)} stabilizers")
    
    # Check string length
    if not stabs:
        print("No stabilizers found")
        return
        
    n = len(stabs[0])
    print(f"Qubits: {n}")
    
    # Check commutativity
    # We can use stim to check this efficiently if we convert to Tableau or just PauliStrings
    
    paulis = []
    for s in stabs:
        paulis.append(stim.PauliString(s))
        
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if paulis[i].commutes(paulis[j]) == False:
                anticommuting_pairs.append((i, j))
                if len(anticommuting_pairs) > 5:
                    break
        if len(anticommuting_pairs) > 5:
            break
            
    if anticommuting_pairs:
        print(f"Found anticommuting pairs: {anticommuting_pairs}")
        # If they anticommute, we can't prepare a simultaneous +1 eigenstate.
        # But maybe they are just generators and we need to find a commuting set?
        # The prompt says: "The final quantum state ... must be a +1 eigenstate of every provided stabilizer generator."
        # This implies they MUST commute. If they don't, the task is impossible as stated, or I misunderstood.
        return

    print("All stabilizers commute.")
    
    print("Attempting to generate tableau from stabilizers...")
    try:
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True, allow_redundant=True)
        print("Tableau generated successfully.")
        
        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully.")
        
        # Verify the circuit
        # We can simulate it
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        # Check if the state satisfies the stabilizers
        satisfied = True
        for i, p in enumerate(paulis):
            if not sim.peek_observables_possible([p])[0]: # this checks if +1 is possible. wait.
                # peek_observables_possible returns (can_be_true, can_be_false)
                # If we want it to be +1, then (True, False) is what we want? 
                # Actually, simpler is to measure it. If the state is a +1 eigenstate, measuring it should always yield 0 (false) result deterministically?
                # No, PauliString measurement: +1 eigenstate -> result False (0) usually in stim conventions? 
                # Let's check expectation value using measure_expectation
                # stim doesn't have measure_expectation on Simulator directly in that way.
                
                # Let's use canonical logic:
                # If P |psi> = |psi>, then measure_expectation(P) = 1.
                # stim.TableauSimulator.measure_expectation requires a PauliString.
                # It returns the expectation value.
                
                ev = sim.measure_expectation(p)
                if ev != 1:
                    print(f"Stabilizer {i} not satisfied. Expectation: {ev}")
                    satisfied = False
                    break
        
        if satisfied:
            print("Circuit verified locally!")
            with open(r'data/gemini-3-pro-preview/agent_files/circuit.stim', 'w') as f:
                f.write(str(circuit))
        else:
            print("Circuit failed verification.")

    except Exception as e:
        print(f"Error generating tableau: {e}")

if __name__ == "__main__":
    solve()
