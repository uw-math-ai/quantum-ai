import stim

def debug_failures():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_114.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    dropped = [38, 92]
    stabilizers = [lines[i] for i in range(len(lines)) if i not in dropped]
    
    # Check 11, 65, 71 in the list
    s11 = lines[11]
    s65 = lines[65]
    s71 = lines[71]
    
    print(f"S11 in list: {s11 in stabilizers}")
    print(f"S65 in list: {s65 in stabilizers}")
    print(f"S71 in list: {s71 in stabilizers}")

    # Generate tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
        print("Tableau generated.")
        
        # Check if tableau satisfies S11
        # Tableau T stabilizes S if T^-1 * S * T is Z...
        # Or easier: create a circuit and simulate measurement.
        
        c = t.to_circuit()
        sim = stim.TableauSimulator()
        sim.do_circuit(c)
        
        # Check expectation values
        for idx in [11, 65, 71]:
            s = stim.PauliString(lines[idx])
            val = sim.peek_observable_expectation(s)
            print(f"Expectation for {idx}: {val}")
            
    except Exception as e:
        print(f"Error: {e}")

debug_failures()
