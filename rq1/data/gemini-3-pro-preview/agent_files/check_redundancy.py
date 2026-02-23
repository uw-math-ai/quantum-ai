import stim
import numpy as np

def check_redundancy():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_114.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    dropped = [38, 92]
    stabilizers = [stim.PauliString(lines[i]) for i in range(len(lines)) if i not in dropped]
    
    # Let's try to add 11, 65, 71 one by one and see if they are independent.
    
    # We can't easily check independence with stim directly without hacking tableau internals.
    # But we can try to prepare a state with a subset and check the others.
    
    # Try preparing state with all EXCEPT 11, 65, 71 (and 38, 92).
    # Then check if 11, 65, 71 are satisfied.
    
    subset_indices = [i for i in range(len(lines)) if i not in dropped and i not in [11, 65, 71]]
    subset_stabs = [stim.PauliString(lines[i]) for i in subset_indices]
    
    t = stim.Tableau.from_stabilizers(subset_stabs, allow_underconstrained=True)
    c = t.to_circuit()
    sim = stim.TableauSimulator()
    sim.do_circuit(c)
    
    print("Checking 11, 65, 71 against subset state:")
    for idx in [11, 65, 71]:
        s = stim.PauliString(lines[idx])
        val = sim.peek_observable_expectation(s)
        print(f"Expectation {idx}: {val}")

check_redundancy()
