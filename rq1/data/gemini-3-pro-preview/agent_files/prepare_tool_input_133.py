import json

def generate_json():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    with open("data/gemini-3-pro-preview/agent_files/circuit_133_cleaned.stim", "r") as f:
        circuit = f.read().strip()
        
    output = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    generate_json()
