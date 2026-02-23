import stim
import sys
import os

def solve():
    try:
        # 1. Read stabilizers
        filename = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_45.txt"
        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        stabilizers = []
        for line in lines:
            try:
                stabilizers.append(stim.PauliString(line))
            except Exception as e:
                print(f"Error parsing line '{line}': {e}")
                return

        print(f"Loaded {len(stabilizers)} stabilizers.")
        if not stabilizers:
            print("No stabilizers found.")
            return

        num_qubits = len(stabilizers[0])
        print(f"Qubits: {num_qubits}")

        # 2. Check commutativity
        anticommuting_pairs = []
        for i in range(len(stabilizers)):
            for j in range(i + 1, len(stabilizers)):
                if not stabilizers[i].commutes(stabilizers[j]):
                    anticommuting_pairs.append((i, j))

        if anticommuting_pairs:
            print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
            for i, j in anticommuting_pairs[:5]:
                print(f"  {i} and {j}: {stabilizers[i]} vs {stabilizers[j]}")
        else:
            print("All stabilizers commute.")

        # 3. Generate Circuit
        print("Generating circuit...")
        # tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True) 
        # The above line might fail if the stabilizers are inconsistent (anticommuting).
        
        if anticommuting_pairs:
            print("Trying to generate a best-effort circuit despite inconsistencies...")
            # We can try to satisfy a maximal commuting subset.
            # But let's see if stim handles it first.
        
        try:
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            circuit = tableau.to_circuit("elimination")
            print("Circuit generated successfully via Tableau.")
        except Exception as e:
            print(f"Tableau generation failed: {e}")
            # Fallback: maybe just initialize to |0> and measure stabilizers? No that prepares a random eigenstate.
            return

        # 4. Verify locally
        print("Verifying locally...")
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        satisfied = 0
        failed_indices = []
        for i, s in enumerate(stabilizers):
            # measure_observable returns the measurement outcome.
            # If the state is a +1 eigenstate, outcome is consistently 0 (False).
            # If -1 eigenstate, outcome is 1 (True).
            # If mixed state (anticommutes with current stabilizers), outcome is random.
            # Since we start from |0> and apply unitary, it's a pure state.
            # So the outcome is deterministic for commuting observables.
            res = sim.peek_observable_expectation(s)
            
            if res == 1: # +1 eigenvalue
                satisfied += 1
            elif res == -1: # -1 eigenvalue
                print(f"Stabilizer {i} failed (eigenvalue -1)")
                failed_indices.append(i)
            else: # 0 means expectation 0, i.e., random outcome
                print(f"Stabilizer {i} failed (expectation 0, indeterminate)")
                failed_indices.append(i)

        print(f"Locally satisfied {satisfied}/{len(stabilizers)} stabilizers.")
        
        output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_45.stim"
        with open(output_path, "w") as f:
            f.write(str(circuit))
        print(f"Circuit written to {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    solve()
