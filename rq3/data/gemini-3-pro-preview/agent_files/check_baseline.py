
import stim

def check():
    print("Loading stabilizers...")
    with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/gemini-3-pro-preview/agent_files/target_stabilizers.txt", "r") as f:
        stabilizers = [stim.PauliString(l.strip()) for l in f if l.strip()]

    print("Loading baseline...")
    with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/gemini-3-pro-preview/agent_files/baseline.stim", "r") as f:
        circuit = stim.Circuit(f.read())

    print("Simulating...")
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)

    failures = 0
    for i, s in enumerate(stabilizers):
        exp = sim.peek_observable_expectation(s)
        if exp != 1:
            print(f"Stabilizer {i} failed. Expectation: {exp}")
            failures += 1
            if failures < 5:
                print(f"  {s}")

    if failures == 0:
        print("All stabilizers preserved by baseline.")
    else:
        print(f"Baseline failed to preserve {failures} stabilizers.")

check()
