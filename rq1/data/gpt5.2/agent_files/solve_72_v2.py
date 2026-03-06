import stim

def solve():
    try:
        with open("data/gemini-3-pro-preview/agent_files/stabilizers_72.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            stabilizers = lines
    except FileNotFoundError:
        print("Stabilizers file not found")
        return

    print(f"Number of stabilizers: {len(stabilizers)}")
    
    # Try to solve using stim.Tableau.from_stabilizers
    try:
        # Note: default method for to_circuit is elimination
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        
        # Try graph state decomposition
        print("Generating circuit using 'graph_state' method...")
        try:
            c = t.to_circuit("graph_state")
            print("Circuit generated.")
        except Exception as e:
            print(f"Graph state generation failed: {e}")
            c = t.to_circuit("elimination")
            print("Using elimination instead.")
        
        # Validate locally
        print("Validating...")
        s = stim.TableauSimulator()
        s.do_circuit(c)
        preserved = 0
        for stab in stabilizers:
            if s.peek_observable_expectation(stim.PauliString(stab)) == 1:
                preserved += 1
        
        print(f"Preserved: {preserved}/{len(stabilizers)}")
        
        if preserved == len(stabilizers):
            with open("circuit_72_v2.stim", "w") as f:
                f.write(str(c))
            print("Success! Circuit saved to circuit_72_v2.stim")
        else:
             print("Failed to preserve all stabilizers.")

    except Exception as e:
        print(f"Failed to generate circuit: {e}")

if __name__ == "__main__":
    solve()
