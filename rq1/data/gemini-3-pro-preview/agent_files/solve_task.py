import stim
import sys

def solve():
    try:
        filename = "data/gemini-3-pro-preview/agent_files/stabilizers_90.txt"
        with open(filename, "r") as f:
            stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]

        print(f"Number of stabilizers: {len(stabilizers)}")
        if not stabilizers:
            print("No stabilizers found!")
            return

        num_qubits = len(stabilizers[0])
        print(f"Num qubits: {num_qubits}")

        # Parse stabilizers
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Check lengths
        lengths = set(len(s) for s in pauli_stabilizers)
        print(f"Stabilizer lengths: {lengths}")
        
        if len(lengths) > 1:
            print("Error: Stabilizers have different lengths!")
            return

        # Create tableau
        # Using allow_underconstrained=True allows fewer than N stabilizers.
        # Using allow_redundant=True allows dependent stabilizers (as long as they are consistent).
        # If they are inconsistent, this will raise an error.
        try:
            tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
        except Exception as e:
            print(f"Failed to create tableau: {e}")
            # If it fails, maybe there are inconsistencies.
            return

        print("Tableau created successfully.")
        
        # Generate circuit
        # method="elimination" uses Gaussian elimination to prepare the state.
        circuit = tableau.to_circuit("elimination")
        
        # Verify locally
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        all_good = True
        for i, s in enumerate(pauli_stabilizers):
            # measure_observable returns the measurement result (0 or 1).
            # We want the state to be a +1 eigenstate, so result should be 0 (false).
            # If the stabilizer is -S, then measuring S would give 1. But here we assume input strings are +1 generators.
            if sim.measure_observable(s) != 0:
                print(f"Failed stabilizer {i}: {s}")
                all_good = False
                break
        
        if all_good:
            print("Circuit satisfies all stabilizers locally.")
            with open("data/gemini-3-pro-preview/agent_files/circuit_90.stim", "w") as out:
                out.write(str(circuit))
            print("Circuit generated and saved to data/gemini-3-pro-preview/agent_files/circuit_90.stim")
        else:
            print("Circuit failed local verification.")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    solve()
