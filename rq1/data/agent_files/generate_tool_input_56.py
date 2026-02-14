import json

def generate_tool_call():
    with open("circuit_candidate_56.stim", "r") as f:
        circuit_str = f.read()
    
    with open("stabilizers_56.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    tool_call = {
        "circuit": circuit_str,
        "stabilizers": stabs
    }
    
    print(json.dumps(tool_call))

if __name__ == "__main__":
    generate_tool_call()
