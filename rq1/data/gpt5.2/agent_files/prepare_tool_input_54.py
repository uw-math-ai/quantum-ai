import json
import os

def prepare():
    try:
        with open("circuit_54.stim", "r") as f:
            circuit = f.read()
    except FileNotFoundError:
        print("circuit_54.stim not found")
        return
        
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabs_54.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("stabs_54.txt not found")
        return
        
    output = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }
    
    with open("tool_input_54.json", "w") as f:
        json.dump(output, f, indent=2)
        
    print("tool_input_54.json created")

if __name__ == "__main__":
    prepare()
