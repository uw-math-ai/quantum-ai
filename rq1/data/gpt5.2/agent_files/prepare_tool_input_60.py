import json
import os

def prepare():
    # Use absolute paths
    stab_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_60.txt"
    circ_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_60.stim"
    
    with open(stab_path, "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    with open(circ_path, "r") as f:
        circuit = f.read()
        
    print(json.dumps({"circuit": circuit, "stabilizers": stabilizers}))

if __name__ == "__main__":
    prepare()
