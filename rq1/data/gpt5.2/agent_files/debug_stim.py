import stim

s = ["XX", "ZZ"]
try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(x) for x in s], allow_underconstrained=True)
    circuit = tableau.to_circuit("elimination")
    print("Circuit:")
    print(circuit)
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    v1 = sim.measure_observable(stim.PauliString("XX"))
    v2 = sim.measure_observable(stim.PauliString("ZZ"))
    print(f"XX: {v1}")
    print(f"ZZ: {v2}")
except Exception as e:
    print(e)
