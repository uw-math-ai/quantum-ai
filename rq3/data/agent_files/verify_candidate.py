import stim
import sys

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    for instruction in circuit:
        if instruction.name in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK", "R", "RX", "RY", "RZ", "M", "MX", "MY", "MZ", "MPP"]:
            continue
            
        n_targets = len(instruction.targets_copy())
        if instruction.name in ["CX", "CNOT"]:
            gates = n_targets // 2
            cx_count += gates
            volume += gates
        elif instruction.name in ["CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            gates = n_targets // 2
            volume += gates
        else:
            # Single qubit gates
            volume += n_targets
            
    return cx_count, volume

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    preserved = 0
    total = len(stabilizers)
    
    for s in stabilizers:
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
            
    return preserved, total

def main():
    if len(sys.argv) < 3:
        print("Usage: python verify_candidate.py <circuit_file> <stabilizers_file>")
        return

    circuit_file = sys.argv[1]
    stabilizers_file = sys.argv[2]

    try:
        with open(circuit_file, "r") as f:
            c_text = f.read()
        circuit = stim.Circuit(c_text)
        
        with open(stabilizers_file, "r") as f:
            stabilizers = [stim.PauliString(line.strip()) for line in f if line.strip()]
            
        cx, vol = count_metrics(circuit)
        preserved, total = check_stabilizers(circuit, stabilizers)
        
        print(f"File: {circuit_file}")
        print(f"CX Count: {cx}")
        print(f"Volume: {vol}")
        print(f"Stabilizers Preserved: {preserved}/{total}")
        print(f"Valid: {preserved == total}")
        
    except Exception as e:
        print(f"Error processing {circuit_file}: {e}")

if __name__ == "__main__":
    main()

