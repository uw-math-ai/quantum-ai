import json

def prepare_input():
    stabilizers = []
    with open("target_stabilizers_102.txt", "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if ". " in line:
                line = line.split(". ")[1]
            stabilizers.append(line)
    
    with open("circuit_102.stim", "r") as f:
        circuit = f.read()

    # Just print the arguments for the tool
    # But the tool takes arguments as a dictionary.
    # I will print them in a format I can easily use to construct the tool call.
    print("STABILIZERS_START")
    print(json.dumps(stabilizers))
    print("STABILIZERS_END")
    print("CIRCUIT_START")
    print(circuit)
    print("CIRCUIT_END")

if __name__ == "__main__":
    prepare_input()
