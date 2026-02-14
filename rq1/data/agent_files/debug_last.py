s6 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX"
s34 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ"

# Print last 10 chars
print(f"s6 end:  {s6[-10:]}")
print(f"s34 end: {s34[-10:]}")

# Check commutation of last few qubits
import stim
p6 = stim.PauliString(s6)
p34 = stim.PauliString(s34)
print(f"Commutes: {p6.commutes(p34)}")
