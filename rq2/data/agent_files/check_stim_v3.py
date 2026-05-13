import stim
t = stim.Tableau(2)
try:
    g = stim.Tableau.from_named_gate("H")
    t.prepend(g, [0])
    print("prepend with gate tableau works")
except Exception as e:
    print(f"prepend failed: {e}")
