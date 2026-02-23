import stim

def verify():
    with open("data/stabilizers_36.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    try:
        with open("circuit_36_new.stim", "r") as f:
            circuit_text = f.read()
        circuit = stim.Circuit(circuit_text)
    except FileNotFoundError:
        print("Circuit file not found.")
        return

    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    all_good = True
    for s_str in stabilizers:
        p = stim.PauliString(s_str)
        # expectation_value returns +1 or -1 (or 0 if random outcome).
        # Since these are stabilizers, they should have definite value +1.
        val = sim.peek_observable_expectation(p)
        if val != 1:
            print(f"Stabilizer {s_str} failed! Expectation: {val}")
            all_good = False
            
    if all_good:
        print("All stabilizers verified locally!")
    else:
        print("Some stabilizers failed verification.")

if __name__ == "__main__":
    verify()
