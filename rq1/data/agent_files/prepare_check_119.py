import json

def get_data():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\target_stabilizers_119_v4.txt", 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_119_v4.stim", 'r') as f:
        circuit = f.read()
        
    print(json.dumps({"circuit": circuit, "stabilizers": stabs}))

if __name__ == "__main__":
    get_data()
