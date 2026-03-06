import json

def prepare():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    with open("data/gemini-3-pro-preview/agent_files/circuit_75_short.stim", "r") as f:
        circuit = f.read()
        
    print(json.dumps({"circuit": circuit, "stabilizers": stabs}))

if __name__ == "__main__":
    prepare()
