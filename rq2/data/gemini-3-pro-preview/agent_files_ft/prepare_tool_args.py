import stim
import json
import os

def main():
    circuit_path = "data/gemini-3-pro-preview/agent_files_ft/input_circuit.stim"
    stabs_path = "data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt"
    
    with open(circuit_path, "r") as f:
        circuit_str = f.read().strip()
    
    with open(stabs_path, "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Assuming all qubits 0..67 are data qubits
    data_qubits = list(range(68))
    flag_qubits = [] # No flags initially

    output = {
        "circuit": circuit_str,
        "data_qubits": data_qubits,
        "flag_qubits": flag_qubits,
        "stabilizers": stabilizers
    }
    
    # Save to a file so I can read it
    with open("data/gemini-3-pro-preview/agent_files_ft/tool_args.json", "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    main()
