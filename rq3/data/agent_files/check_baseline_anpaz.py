import stim
import sys

def check_baseline():
    try:
        with open("current_target_stabilizers.txt", "r") as f:
            lines = f.readlines()
        
        stabs_str = []
        for line in lines:
            line = line.strip().replace(" ", "")
            if line:
                if line.endswith(','):
                    line = line[:-1]
                parts = line.split(',')
                stabs_str.extend(parts)
            
        stabs_str = [s for s in stabs_str if s]
        pauli_stabs = [stim.PauliString(s) for s in stabs_str]
        
        with open("current_baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
            
        sim = stim.TableauSimulator()
        sim.do_circuit(baseline)
        
        preserved = 0
        failed = 0
        failed_indices = []
        for i, s in enumerate(pauli_stabs):
            if sim.peek_observable_expectation(s) == 1:
                preserved += 1
            else:
                failed += 1
                failed_indices.append(i)
                print(f"Stabilizer {i} not preserved.")

        print(f"Baseline preserves {preserved}/{len(pauli_stabs)} stabilizers.")
        
        # Check anticommutation
        print("Checking anticommutation among stabilizers...")
        for i in range(len(pauli_stabs)):
            for j in range(i+1, len(pauli_stabs)):
                if not pauli_stabs[i].commutes(pauli_stabs[j]):
                    print(f"Stabilizer {i} anticommutes with Stabilizer {j}")
                    if i in failed_indices:
                        print(f"  (Stabilizer {i} failed in baseline)")
                    if j in failed_indices:
                        print(f"  (Stabilizer {j} failed in baseline)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_baseline()
