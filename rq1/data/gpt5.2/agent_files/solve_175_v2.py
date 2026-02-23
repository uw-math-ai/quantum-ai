import stim
import sys

def solve():
    try:
        with open("stabilizers_175.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("stabilizers_175.txt not found")
        return

    print(f"Number of stabilizers: {len(stabilizers)}")
    if len(stabilizers) == 0:
        return

    paulis = [stim.PauliString(s) for s in stabilizers]
    
    try:
        # Use Stim's tableau method
        # allow_redundant=True is crucial because 202 > 175
        # allow_underconstrained=True is also good in case we don't fix all degrees of freedom (though with 202 stabilizers likely we do)
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True, allow_redundant=True)
        
        circuit = tableau.to_circuit("elimination")
        
        # Verify internally
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        failed = False
        for i, p in enumerate(paulis):
            if sim.measure_observable(p) != 0:
                print(f"Failed to stabilize index {i}: {stabilizers[i]}")
                failed = True
                break
        
        if not failed:
            print("Circuit successfully prepares the state (internal check passed).")
            with open("circuit_175.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Circuit generation failed internal verification.")

    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
