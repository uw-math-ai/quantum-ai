import json

def generate():
    with open('stabilizers_105_v2.txt', 'r') as f:
        stabilizers = [l.strip() for l in f if l.strip()]
    
    with open('circuit_105_v2.stim', 'r') as f:
        circuit = f.read()
        
    print(json.dumps({"stabilizers": stabilizers, "circuit": circuit}))

if __name__ == "__main__":
    generate()
