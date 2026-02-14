import stim
try:
    t = stim.Tableau(1)
    c = t.to_circuit("elimination")
    print("Method to_circuit exists!")
except AttributeError:
    print("Method to_circuit DOES NOT exist.")
except Exception as e:
    print(f"Other error: {e}")
