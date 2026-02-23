import stim
try:
    s = [stim.PauliString("X"), stim.PauliString("Z")]
    t = stim.Tableau.from_stabilizers(s, allow_underconstrained=True)
    print("Success")
except Exception as e:
    print(f"Failed: {e}")
