import stim
try:
    c = stim.Circuit.from_file("candidate_1.stim")
    print("Valid")
    print(c)
except Exception as e:
    print(f"Invalid: {e}")