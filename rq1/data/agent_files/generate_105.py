import json

def generate_json():
    with open('stabilizers_105.txt', 'r') as f:
        stabilizers = [l.strip() for l in f if l.strip()]
    
    with open('circuit_105.stim', 'r') as f:
        circuit_text = f.read()
    
    data = {
        "circuit": circuit_text,
        "stabilizers": stabilizers
    }
    
    print(json.dumps(data))

if __name__ == "__main__":
    generate_json()
