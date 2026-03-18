import stim

print("Stim version:", stim.__version__)

stabs = ["XX", "ZZ"]
try:
    t = stim.Tableau.from_stabilizers(stabs, allow_redundant=True, allow_underconstrained=True)
    print("Small example success")
except Exception as e:
    print("Small example failed:", e)

try:
    print("Trying without kwargs:")
    t = stim.Tableau.from_stabilizers(stabs)
    print("Without kwargs success")
except Exception as e:
    print("Without kwargs failed:", e)

try:
    print("Trying with PauliString:")
    ps = [stim.PauliString(s) for s in stabs]
    t = stim.Tableau.from_stabilizers(ps, allow_redundant=True, allow_underconstrained=True)
    print("With PauliString success")
except Exception as e:
    print("With PauliString failed:", e)
