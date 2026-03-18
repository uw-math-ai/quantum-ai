import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets) // 2
    return count

def compute_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I", "SWAP", "ISWAP"]:
            if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP"]:
                count += len(instr.targets) // 2
            else:
                count += len(instr.targets)
    return count

def main():
    try:
        # Load stabilizers
        with open("stabilizers_task.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Load candidate
        with open("candidate_circuit.stim", "r") as f:
            circuit_str = f.read()
            circuit = stim.Circuit(circuit_str)
            
        cx = count_cx(circuit)
        vol = compute_volume(circuit)
        print(f"Candidate CX: {cx}")
        print(f"Candidate Volume: {vol}")
        
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        failed = 0
        for s_str in stabilizers:
            s = stim.PauliString(s_str)
            if sim.peek_observable_expectation(s) != 1:
                failed += 1
                
        if failed == 0:
            print(f"VALID: All {len(stabilizers)} stabilizers preserved.")
        else:
            print(f"INVALID: {failed}/{len(stabilizers)} stabilizers failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
