import json

def prepare_tool_input():
    with open("circuit_kept.stim", "r") as f:
        circuit = f.read()
    
    with open("stabilizers_148.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    print("CIRCUIT_START")
    print(circuit)
    print("CIRCUIT_END")
    
    # I don't need to print stabilizers, I know they are in the file I wrote.
    # But to be safe I will just reference the file I wrote in previous turns?
    # No, I need to include them in the tool call.
    # There are 146 stabilizers.
    
    # output the list as json for easy copying
    print("STABILIZERS_JSON_START")
    print(json.dumps(stabilizers))
    print("STABILIZERS_JSON_END")

if __name__ == "__main__":
    prepare_tool_input()
