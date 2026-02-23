import json
import os

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read().strip()

def generate_json():
    base_dir = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files'
    circuit = read_file(os.path.join(base_dir, 'circuit_105.stim'))
    stabs_content = read_file(os.path.join(base_dir, 'stabilizers_105.txt'))
    stabs = [line.strip() for line in stabs_content.splitlines() if line.strip()]
    
    # Just print the circuit and stabilizers separately to avoid huge JSON block
    # Actually, print the circuit as a single string (escaped newlines) so I can copy it.
    # And print the stabilizers as a python list.
    
    print("CIRCUIT_JSON_START")
    print(json.dumps(circuit))
    print("CIRCUIT_JSON_END")
    
    # stabilizers is already a list in the file, basically
    print("STABILIZERS_START")
    print(json.dumps(stabs))
    print("STABILIZERS_END")

if __name__ == "__main__":
    generate_json()
