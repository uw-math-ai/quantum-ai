import stim
import sys

def verify():
    # Load stabilizers
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_119_v2.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Load circuit
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_119.stim', 'r') as f:
        circuit = stim.Circuit(f.read())

    print(f"Loaded {len(stabilizers)} stabilizers.")

    sim = stim.TableauSimulator()
    sim.do(circuit)

    # Check each stabilizer
    failed = []
    for i, s in enumerate(stabilizers):
        p = stim.PauliString(s)
        ex = sim.peek_observable_expectation(p)
        if ex != 1:
            failed.append((i, s, ex))
            
    if failed:
        print(f"Failed {len(failed)} stabilizers:")
        for idx, s, ex in failed:
            print(f"{idx}: {ex} for {s}")
    else:
        print("All stabilizers verified successfully!")

if __name__ == "__main__":
    verify()
