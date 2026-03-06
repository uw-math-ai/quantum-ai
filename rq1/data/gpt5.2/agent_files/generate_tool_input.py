import json

def generate_input():
    with open('data/gemini-3-pro-preview/agent_files/circuit_115.stim', 'r') as f:
        circuit = f.read()
    
    with open('data/gemini-3-pro-preview/agent_files/stabilizers.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    tool_input = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }
    
    print(json.dumps(tool_input))

if __name__ == "__main__":
    generate_input()
