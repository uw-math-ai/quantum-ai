import stim
try:
    s = "XZZXIIII"
    p = stim.PauliString(s)
    print(f"Created PauliString: {p}")
    t = stim.Tableau.from_stabilizers([p], allow_underconstrained=True)
    print("Created Tableau")
except Exception as e:
    import traceback
    traceback.print_exc()
