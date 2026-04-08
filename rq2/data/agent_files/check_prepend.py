import stim
t = stim.Tableau(1)
try:
    t.prepend("H", [0])
    print("prepend(name, targets) works")
except:
    try:
        t.prepend(stim.Tableau.from_named_gate("H"))
        print("prepend(tableau) works")
    except Exception as e:
        print(f"prepend failed: {e}")
