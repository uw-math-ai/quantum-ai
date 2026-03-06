import json

def prepare():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_171_new.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_171_best.stim", "r") as f:
        circuit = f.read()
        
    data = {
        "circuit": circuit,
        "stabilizers": stabs
    }
    
    # Write to a new file to avoid reading the old one
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\tool_input_171_v2.json", "w") as f:
        json.dump(data, f)
        
if __name__ == "__main__":
    prepare()
