import stim
print(dir(stim.Tableau))
try:
    t = stim.Tableau(1)
    print(t.to_circuit(method="elimination"))
    print(t.to_circuit(method="graph_state"))
except Exception as e:
    print(e)
