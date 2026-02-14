import stim
import sys

def verify():
    # Load circuit
    try:
        with open("circuit_102.stim", "r") as f:
            circuit_text = f.read()
        circuit = stim.Circuit(circuit_text)
    except Exception as e:
        print(f"Error loading circuit: {e}")
        return

    # Load stabilizers
    try:
        with open("target_stabilizers_102.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    stabilizers = []
    for line in lines:
        if ". " in line:
            line = line.split(". ")[1]
        stabilizers.append(stim.PauliString(line))

    # Simulate
    simulator = stim.TableauSimulator()
    simulator.do(circuit)

    # Check stabilizers
    all_good = True
    failed_count = 0
    for i, stab in enumerate(stabilizers):
        expectation = simulator.peek_observable_expectation(stab)
        if expectation != 1:
            print(f"Stabilizer {i+1} failed: expectation {expectation}")
            failed_count += 1
            all_good = False
            # break # Don't break

    if all_good:
        print("All stabilizers preserved!")
    else:
        print(f"{failed_count} stabilizers failed.")

if __name__ == "__main__":
    verify()
