import stim
try:
    t = stim.Tableau(1)
    c = t.to_circuit(method="graph_state")
    print("Graph state method exists")
except Exception as e:
    print(f"Graph state method failed: {e}")
