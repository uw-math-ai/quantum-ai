import stim
try:
    with open("circuit_input.stim", "r") as f:
        c = f.read()
    stim.Circuit(c)
    print("Circuit is valid Stim.")
except Exception as e:
    print(f"Circuit error: {e}")
