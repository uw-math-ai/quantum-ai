import json
import sys

def prepare_tool_input():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_63.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_63.stim", "r") as f:
        circuit = f.read()

    # Create the JSON object
    data = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }

    # Write to a file so I can verify it or just print it to copy
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\tool_input_63.json", "w") as f:
        json.dump(data, f, indent=2)
        
    print("Prepared tool_input_63.json")

if __name__ == "__main__":
    prepare_tool_input()
