import stim

s_str = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII"
p = stim.PauliString(s_str)
print(f"Indices of X: {[i for i in range(54) if p[i] == 1]}")
print(f"Indices of Z: {[i for i in range(54) if p[i] == 3]}")
