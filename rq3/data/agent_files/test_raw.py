import stim

def solve_raw():
    lines = []
    with open("current_stabilizers.txt", "r") as f:
        for l in f:
            l = l.strip().replace(",", "")
            if l:
                lines.append(stim.PauliString(l))
    
    tableau = stim.Tableau.from_stabilizers(lines, allow_underconstrained=True)
    circuit = tableau.to_circuit(method="graph_state")
    
    # Test raw circuit
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    for stab in lines:
        if sim.peek_observable_expectation(stab) == 1:
            preserved += 1
            
    print(f"Raw circuit preserved: {preserved}/{len(lines)}")
    
    # Also check if method="elimination" works
    circuit2 = tableau.to_circuit(method="elimination")
    sim2 = stim.TableauSimulator()
    sim2.do(circuit2)
    preserved2 = 0
    for stab in lines:
        if sim2.peek_observable_expectation(stab) == 1:
            preserved2 += 1
    print(f"Elimination circuit preserved: {preserved2}/{len(lines)}")

if __name__ == "__main__":
    solve_raw()
