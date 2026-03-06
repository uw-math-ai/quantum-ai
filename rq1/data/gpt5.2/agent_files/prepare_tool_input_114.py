import json

def prepare():
    with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_114.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    with open("circuit_114.stim", "r") as f:
        circuit = f.read()

    data = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }

    with open("tool_input_114.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print("Prepared tool_input_114.json")

if __name__ == "__main__":
    prepare()
