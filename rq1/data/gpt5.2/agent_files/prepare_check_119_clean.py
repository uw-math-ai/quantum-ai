import json
import stim

def generate_tool_input():
    with open("circuit_119.stim", "r") as f:
        circuit_str = f.read()
    
    with open("stabilizers_119.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Validate that we don't have weird characters
    for s in stabilizers:
        if len(s) != 119:
            print(f"Warning: stabilizer length {len(s)} != 119: {s}")

    tool_input = {
        "circuit": circuit_str,
        "stabilizers": stabilizers
    }
    
    # Print the JSON to stdout so I can see it, but ensure no line breaks in strings
    json_str = json.dumps(tool_input)
    print(json_str)

if __name__ == "__main__":
    generate_tool_input()
