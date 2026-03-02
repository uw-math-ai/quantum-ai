import json
import sys

def prepare_input():
    with open("circuit_155.stim", "r") as f:
        circuit_str = f.read()

    with open("stabilizers_155.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    data = {
        "circuit": circuit_str,
        "stabilizers": stabilizers
    }

    with open("tool_input_155.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    prepare_input()
