import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets) // 2
    return count

def analyze():
    with open("baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    with open("target_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Baseline CX count: {count_cx(baseline)}")
    print(f"Number of stabilizers: {len(stabilizers)}")
    print(f"Number of qubits in stabilizers: {len(stabilizers[0])}")
    
    # Check if stabilizers are independent
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    print("Tableau created successfully")
    print(f"Tableau qubits: {len(tableau)}")

    # Try synthesis
    try:
        synth_circuit = tableau.to_circuit("graph_state")
        print(f"Synthesized graph state circuit CX count: {count_cx(synth_circuit)}")
        
        synth_circuit_std = tableau.to_circuit("method1") # default method
        print(f"Synthesized standard circuit CX count: {count_cx(synth_circuit_std)}")

    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    analyze()
