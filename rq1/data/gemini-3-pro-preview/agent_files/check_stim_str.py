import stim
targets = [i for i in range(32)]
inst = stim.CircuitInstruction("CX", targets)
print(f"'{inst}'")
