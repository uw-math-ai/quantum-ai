import stim
try:
    help(stim.Tableau.to_circuit)
except:
    print("to_circuit help failed")
try:
    print(stim.Tableau.to_circuit.__doc__)
except:
    print("to_circuit doc failed")
