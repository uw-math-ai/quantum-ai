import json

def prepare():
    # Read the circuit
    with open("circuit_171.stim", "r") as f:
        circuit = f.read()

    # Read the stabilizers
    with open("stabilizers_171.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Construct the arguments for the tool
    tool_args = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }

    # Print as JSON string for me to use in the tool call
    print(json.dumps(tool_args))

if __name__ == "__main__":
    prepare()
