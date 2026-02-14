import stim
try:
    print(f"Stim version: {stim.__version__}")
    stabs = [stim.PauliString("XX"), stim.PauliString("ZZ")]
    tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
