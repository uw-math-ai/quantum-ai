import stim
try:
    c = stim.Circuit("H 0")
    t = stim.Tableau.from_circuit(c)
    t.to_circuit(method="graph_state")
    print("graph_state method exists")
except Exception as e:
    print(f"graph_state method failed: {e}")
