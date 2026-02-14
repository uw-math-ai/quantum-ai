import json

def generate_input():
    with open("circuit_161.stim", "r") as f:
        circuit = f.read()
    
    with open("stabilizers_161.txt", "r") as f:
        # Stabilizers is an array of strings
        stabilizers = [line.strip() for line in f if line.strip()]
        
    tool_input = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }
    
    with open("tool_input.json", "w") as f:
        json.dump(tool_input, f)
        
    print("tool_input.json created")

if __name__ == "__main__":
    generate_input()
