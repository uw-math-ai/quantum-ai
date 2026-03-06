
import stim
import sys
import os

# Set working directory to file location to find files
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets_copy()) // 2
    return count

def count_volume(circuit):
    # Volume is total gate count
    count = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
            if instruction.name in ["CX", "CNOT", "CZ"]:
                count += len(instruction.targets_copy()) // 2
            else:
                count += len(instruction.targets_copy())
    return count

def main():
    print("Loading baseline...")
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    print(f"Baseline CX count: {count_cx(baseline)}")
    print(f"Baseline volume: {count_volume(baseline)}")
    
    print("Loading stabilizers...")
    with open("target_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    # Check number of qubits
    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}")
    
    print("Creating tableau from stabilizers...")
    try:
        # Convert strings to PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    print("Synthesizing circuit...")
    # Try different synthesis methods if available or just the default
    # Note: stim.Tableau.to_circuit() returns a circuit that implements the tableau operation.
    # If the tableau maps Z basis to stabilizers, applying it to |0> prepares the state.
    
    # Method 1: Default (Gaussian elimination)
    synth_circuit = tableau.to_circuit(method="elimination")
    
    print(f"Synthesized CX count: {count_cx(synth_circuit)}")
    print(f"Synthesized volume: {count_volume(synth_circuit)}")
    
    # Save synthesized circuit
    with open("synthesized.stim", "w") as f:
        f.write(str(synth_circuit))
        
    if count_cx(synth_circuit) < count_cx(baseline):
        print("IMPROVEMENT FOUND!")
    elif count_cx(synth_circuit) == count_cx(baseline) and count_volume(synth_circuit) < count_volume(baseline):
        print("IMPROVEMENT FOUND (Volume)!")
    else:
        print("No improvement with default synthesis.")

    # Try graph state synthesis?
    # Stim's tableau.to_circuit("graph_state") is often efficient for stabilizer states.
    try:
        graph_circuit = tableau.to_circuit(method="graph_state")
        print(f"Graph state CX count: {count_cx(graph_circuit)}")
        print(f"Graph state volume: {count_volume(graph_circuit)}")
        
        with open("graph_state.stim", "w") as f:
            f.write(str(graph_circuit))
            
        if count_cx(graph_circuit) < count_cx(baseline):
            print("GRAPH STATE IMPROVEMENT FOUND!")
        elif count_cx(graph_circuit) == count_cx(baseline) and count_volume(graph_circuit) < count_volume(baseline):
            print("GRAPH STATE IMPROVEMENT FOUND (Volume)!")
    except Exception as e:
        print(f"Graph state synthesis failed or not supported: {e}")

if __name__ == "__main__":
    main()
