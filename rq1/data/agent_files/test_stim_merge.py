import stim
try:
    c = stim.Circuit()
    c.append('CX', [0, 1])
    c.append('CX', [0, 2])
    print(f"Circuit:\n{c}")
except Exception as e:
    print(f"Error: {e}")
