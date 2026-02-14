import stim
import sys

def check():
    try:
        with open("circuit_54.stim", "r") as f:
            circuit_text = f.read()
        circuit = stim.Circuit(circuit_text)
    except Exception as e:
        print(f"Failed to load circuit: {e}")
        return

    with open("stabilizers_54.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Checking {len(stabilizers)} stabilizers...")
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    failed = 0
    for i, s in enumerate(stabilizers):
        p = stim.PauliString(s)
        if sim.measure_observable(p):
            # print(f"Stabilizer {i} failed")
            failed += 1
    
    print(f"Failed: {failed}")
    print(f"Total: {len(stabilizers)}")

if __name__ == "__main__":
    check()
