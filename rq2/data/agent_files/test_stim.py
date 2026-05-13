
import stim
c = stim.Circuit("H 0")
t = stim.Tableau.from_circuit(c)
print(t)
p = stim.PauliString("X")
print(p)
