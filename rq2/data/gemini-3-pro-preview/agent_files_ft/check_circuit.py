import sys
import stim

def parse_stabilizers(filepath):
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def run_validation():
    try:
        # Load circuit
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input.stim", 'r') as f:
            circuit_str = f.read()
        
        # Load stabilizers
        stabs = parse_stabilizers(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt")
        
        # Determine data qubits (using max qubit index from circuit)
        circuit = stim.Circuit(circuit_str)
        num_qubits = circuit.num_qubits
        data_qubits = list(range(num_qubits)) # Assuming all are data qubits initially
        
        print(f"Num qubits: {num_qubits}")
        
    except Exception as e:
        print(f"Error parsing: {e}")

if __name__ == "__main__":
    run_validation()
