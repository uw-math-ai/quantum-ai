import json

def prepare_input():
    with open("stabilizers_124.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    with open("circuit_124_new.stim", "r") as f:
        circuit = f.read()
        
    tool_input = {
        "stabilizers": stabs,
        "circuit": circuit
    }
    
    with open("tool_input_124.json", "w") as f:
        json.dump(tool_input, f)

if __name__ == "__main__":
    prepare_input()
