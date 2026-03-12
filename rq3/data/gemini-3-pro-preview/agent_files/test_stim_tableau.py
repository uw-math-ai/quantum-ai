import stim
t = stim.Tableau(1)
print(f"Tableau(1) to circuit: {t.to_circuit()}")
t2 = t.then(stim.Circuit("H 0").to_tableau())
print(f"Tableau(1).then(H) to circuit: {t2.to_circuit()}")
