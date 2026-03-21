import json
import os

def load_file(path):
    with open(path, 'r') as f:
        return f.read().strip()

def load_lines(path):
    with open(path, 'r') as f:
        return [l.strip() for l in f.readlines() if l.strip()]

def main():
    base_dir = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft"
    circuit = load_file(os.path.join(base_dir, "circuit.stim"))
    stabilizers = load_lines(os.path.join(base_dir, "stabilizers_fixed.txt"))
    
    # Calculate data qubits from stabilizer length
    stab_len = len(stabilizers[0])
    data_qubits = list(range(stab_len))
    
    flag_qubits = []

    tool_args = {
        "circuit": circuit,
        "stabilizers": stabilizers,
        "data_qubits": data_qubits,
        "flag_qubits": flag_qubits
    }
    
    print(json.dumps(tool_args))

if __name__ == "__main__":
    main()
