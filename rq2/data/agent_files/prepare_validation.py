import json

def prepare():
    with open("candidate.stim", "r") as f:
        circuit = f.read()
    
    with open("stabilizers_current.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    print("CIRCUIT_START")
    print(circuit)
    print("CIRCUIT_END")
    
    print("STABS_START")
    print(json.dumps(stabs))
    print("STABS_END")
    
    # Flags: 175 to 275
    # Data: 0 to 174
    
if __name__ == "__main__":
    prepare()
