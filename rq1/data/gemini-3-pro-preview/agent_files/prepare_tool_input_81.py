import json

def prepare():
    with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_81.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    with open(r"data\gemini-3-pro-preview\agent_files\circuit_81_new.stim", "r") as f:
        circuit = f.read()

    tool_input = {
        "stabilizers": stabilizers,
        "circuit": circuit
    }

    with open(r"data\gemini-3-pro-preview\agent_files\tool_input_81.json", "w") as f:
        json.dump(tool_input, f, indent=2)
        
    print("Tool input prepared.")

if __name__ == "__main__":
    prepare()
