import stim

def verify():
    # Load circuit
    with open("circuit_84.stim", "r") as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)

    # Load stabilizers
    with open("stabilizers_84.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check stabilizers
    failed = []
    for i, line in enumerate(lines):
        stab = stim.PauliString(line)
        result = sim.peek_observable_expectation(stab)
        if result != 1:
            failed.append((i, line, result))
            print(f"Failed stabilizer {i}: {line} -> expectation {result}")
        else:
            # print(f"Passed stabilizer {i}")
            pass
            
    if not failed:
        print("All stabilizers passed!")
    else:
        print(f"Total failed: {len(failed)}")

if __name__ == "__main__":
    verify()
