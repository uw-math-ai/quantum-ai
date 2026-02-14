import stim

with open("circuit_attempt.stim", "r") as f:
    c_text = f.read()

c = stim.Circuit(c_text)
inv_c = c.inverse()

with open("circuit_attempt_inv.stim", "w") as f:
    f.write(str(inv_c))
print("Inverted circuit saved.")
