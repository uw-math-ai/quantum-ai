import stim

circuit_text = """
H 0
S 3
H 1 4
CX 0 1 0 3 0 4
H 2
CX 2 0 3 1 1 3 3 1
S 1
H 1
CX 3 1 3 2 2 3 3 2
H 2
S 4
H 4
CX 3 2 4 2
H 3
CX 3 4
H 4
CX 4 3
H 1 3
S 1 1 3 3
H 1 3
S 1 1 2 2 3 3 4 4
"""

circuit = stim.Circuit(circuit_text)
print("Circuit loaded.")

target_stabilizers = [
    stim.PauliString("XZZXI"),
    stim.PauliString("IXZZX"),
    stim.PauliString("XIXZZ"),
    stim.PauliString("ZXIXZ")
]

sim = stim.TableauSimulator()
sim.do(circuit)

all_good = True
for s in target_stabilizers:
    ev = sim.peek_observable_expectation(s)
    if ev != 1:
        print(f"Failed stabilizer {s}: expectation {ev}")
        all_good = False
    else:
        print(f"Verified {s}")

if all_good:
    print("SUCCESS: All stabilizers verified.")
else:
    print("FAILURE: Some stabilizers failed.")
