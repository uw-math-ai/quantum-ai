import stim
import sys

def check_commutation(stabilizers):
    n = len(stabilizers)
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if stabilizers[i].commutes(stabilizers[j]) == False:
                anticommuting_pairs.append((i, j))
    return anticommuting_pairs

def solve():
    try:
        # Use absolute path to be safe
        path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt'
        with open(path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(lines)} stabilizers.")
        
        # Parse stabilizers
        stabilizers = []
        for i, line in enumerate(lines):
            try:
                stabilizers.append(stim.PauliString(line))
            except Exception as e:
                print(f"Error parsing line {i}: {line} -> {e}")
                return

        num_qubits = len(stabilizers[0])
        print(f"Number of qubits: {num_qubits}")

        # Check for anticommuting pairs
        print("Checking for anticommuting pairs...")
        pairs = check_commutation(stabilizers)
        if pairs:
            print(f"Found {len(pairs)} anticommuting pairs!")
            for i, j in pairs[:10]:
                print(f"  {i} vs {j}")
            if len(pairs) > 10:
                print("  ...")
            # If anticommuting, we can't form a single state.
            # But maybe we can find a large subset?
            # Or maybe the prompt implies we should fix it? 
            # The prompt says "prepares the stabilizer state defined by these generators".
            # If they don't commute, they don't define a state.
            return

        print("All stabilizers commute.")

        # Try to create a tableau
        try:
            # allow_redundant is important if generators are dependent
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
            print("Tableau created successfully.")
            
            # Convert to circuit
            # "gaussian" method is usually good for preparing state from |0>
            circuit = tableau.to_circuit("gaussian")
            
            out_path = r'data\gemini-3-pro-preview\agent_files\circuit_solution.stim'
            with open(out_path, 'w') as f:
                f.write(str(circuit))
                
            print(f"Circuit generated and saved to {out_path}")
            
            # Verify circuit satisfies stabilizers
            # We can simulate it
            print("Verifying circuit...")
            sim = stim.TableauSimulator()
            sim.do(circuit)
            final_state = sim.current_inverse_tableau() # This is inverted?
            # Or just check if stabilizers are stabilized
            # sim.measure_observables(stabilizers) should all be 0 (deterministic +1)
            
            # Actually, let's use check_stabilizers_tool logic locally if we can,
            # but we don't have the tool code.
            # We can just check if each stabilizer has expectation +1.
            
            all_good = True
            for i, s in enumerate(stabilizers):
                if not sim.peek_observable_expectation(s) == 1:
                    print(f"Stabilizer {i} not satisfied!")
                    all_good = False
                    break
            
            if all_good:
                print("Verification successful: All stabilizers satisfied.")
            else:
                print("Verification failed.")

        except Exception as e:
            print(f"Error creating tableau: {e}")
            
    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    solve()
