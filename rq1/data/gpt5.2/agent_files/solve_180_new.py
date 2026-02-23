import stim
import sys

def check_commutativity(stabilizers):
    paulis = [stim.PauliString(s) for s in stabilizers]
    num_stabs = len(paulis)
    print(f"Number of stabilizers: {num_stabs}")
    print(f"Qubits: {len(paulis[0])}")

    for i in range(num_stabs):
        for j in range(i + 1, num_stabs):
            if not paulis[i].commutes(paulis[j]):
                print(f"Anticommutation found between index {i} and {j}")
                print(f"  {stabilizers[i]}")
                print(f"  {stabilizers[j]}")
                return False
    print("All stabilizers commute.")
    return True

def solve():
    with open("stabilizers_180_new.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if not check_commutativity(lines):
        return

    try:
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in lines], 
            allow_underconstrained=True,
            allow_redundant=True
        )
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully.")
        
        # Verify the circuit
        print("Verifying circuit...")
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        all_good = True
        for i, s in enumerate(lines):
            p = stim.PauliString(s)
            expectation = sim.peek_observable_expectation(p)
            if expectation != 1:
                print(f"Stabilizer {i} failed: {s}")
                print(f"Expectation: {expectation}")
                all_good = False
                break
        
        if all_good:
            print("Verification successful: All stabilizers preserved.")
            with open("circuit_180_new.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Verification failed.")

    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
