import stim
import sys

def solve():
    print("Loading stabilizers...")
    try:
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\data\\agent_files\\target_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        stabs = [stim.PauliString(l) for l in lines]
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    print(f"Loaded {len(stabs)} stabilizers.")

    # Synthesize
    print("Synthesizing...")
    try:
        # allow_underconstrained=True is important if fewer than N stabilizers
        tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit(method="elimination")
    except Exception as e:
        print(f"Error synthesizing: {e}")
        return

    # Verify
    print("Verifying...")
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = True
    for s in stabs:
        if sim.peek_observable_expectation(s) != 1:
            preserved = False
            print(f"Failed to preserve: {s}")
            break
    
    if preserved:
        print("Verification SUCCESS: All stabilizers preserved.")
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\data\\agent_files\\final_candidate.stim", "w") as f:
            f.write(str(circuit))
        print("---CIRCUIT START---")
        print(str(circuit))
        print("---CIRCUIT END---")
    else:
        print("Verification FAILED.")

if __name__ == "__main__":
    solve()
