import stim
from solve_135_try_3 import stabilizers

s0 = stabilizers[0]
s54 = stabilizers[54]

print(f"S0: {s0}")
print(f"S54: {s54}")

p0 = stim.PauliString(s0)
p54 = stim.PauliString(s54)
print(f"Commutes: {p0.commutes(p54)}")
