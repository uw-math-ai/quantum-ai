import json
import stim

def generate_tool_input():
    with open("circuit_119_v3.stim", "r") as f:
        circuit_str = f.read()
    
    with open("stabilizers_119_fixed_v2.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    tool_input = {
        "circuit": circuit_str,
        "stabilizers": stabilizers
    }
    
    # Print the JSON to stdout
    json_str = json.dumps(tool_input)
    print(json_str)

if __name__ == "__main__":
    generate_tool_input()
